
from django.shortcuts import render, get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def product_list(request):
    query = request.GET.get("q", "")

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, "store/product_list.html", {
        "products": products,
        "query": query
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {
        "product": product
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1

    request.session["cart"] = cart

    from django.shortcuts import redirect
    return redirect("cart")


def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        subtotal = product.price * quantity
        total += subtotal

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(request, "store/cart.html", {
        "items": items,
        "total": total,
    })

def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart

    from django.shortcuts import redirect
    return redirect("cart")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("product_list")
    else:
        form = UserCreationForm()

    return render(request, "store/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("product_list")
    else:
        form = AuthenticationForm()

    return render(request, "store/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("product_list")

@login_required
def checkout_view(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))

        if quantity <= 0 or quantity > product.stock:
            return render(request, "store/cart.html", {
                "items": [],
                "total": 0,
                "error": f"Insufficient stock for {product.name}."
            })

        subtotal = product.price * quantity
        total += subtotal
        items.append((product, quantity))

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )

        for product, quantity in items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            product.stock -= quantity
            product.save()

        request.session["cart"] = {}
        return redirect("product_list")

    return render(request, "store/checkout.html", {
        "items": items,
        "total": total
    })
