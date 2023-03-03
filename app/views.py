from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import Customer,Product,Cart,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import stripe
from datetime import datetime
from django.db.models import Q

stripe.api_key = "sk_test_51IWuSRFzvY3Oon8KHXlURApAt4rjhN1qKfh37Xvcwam0uzfvzZt8o3TJCirb5uFParGlho3a15S6V2s0mZLXsaOg00woMU6Fen"


def search_bar(request):
    search_content = request.GET.get('search_content')
    searching = Product.objects.filter(Q(title__icontains=search_content) | Q(description__icontains=search_content) | Q(brand__icontains=search_content) | Q(category__icontains=search_content))

    count_search = searching.count()
    context = {'searching':searching, 'count_search':count_search, 'search_content':search_content}
    return render(request, 'app/search_result.html', context)

class ProductView(View):
    def get(self,request):
        totalitem=0
        gardeningtools=Product.objects.filter(category='GT')
        farmingtools=Product.objects.filter(category='FT')
        tractors=Product.objects.filter(category='T')
        engines=Product.objects.filter(category='E')
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/home.html',{'tractors':tractors,'engines':engines,'gardeningtools':gardeningtools,'farmingtools':farmingtools,'totalitem':totalitem})

class ProductDeatilView(View):
    def get(self,request,pk):
        totalitem=0
        product=Product.objects.get(pk=pk)


        item_already_in_cart=False
        if request.user.is_authenticated:
            item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount = 70.0
    cart_product=[p for p in Cart.objects.all() if p.user==user]
    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity*p.product.selling_price*p.Days)
            amount+=tempamount
            totalamount=amount+shipping_amount

            start_dt = p.Start_date[0:10]
            end_dt = p.End_date[0:10]

            print('start_dt')
            print(start_dt)
            dys = p.Days
        totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/addtocart.html',{'carts':cart,'totalamount':totalamount,'amount':amount,'totalitem':totalitem, 'start_dt':start_dt, 'end_dt':end_dt, 'dys':dys})
    else:
        totalitem = None
        return render(request,'app/emptycart.html',{'totalitem':totalitem})

def plus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount=0.0
        shipping_amount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            tempamount=(p.quantity*p.product.selling_price*p.Days)
            amount+=tempamount
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount+shipping_amount
        }
        return JsonResponse(data)





def minus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount=0.0
        shipping_amount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            tempamount=(p.quantity*p.product.selling_price*p.Days)
            amount+=tempamount
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount+shipping_amount
        }
        return JsonResponse(data)

@csrf_exempt
def save_days(request):
    id_start_date = request.POST.get('id_start_date')
    id_end_date = request.POST.get('id_end_date')
    days = request.POST.get('days')

    print('sow    ssss')
    print(id_start_date, id_end_date, days)

    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == user]
    if cart_product:
        for p in cart_product:

            p.Start_date =id_start_date
            p.End_date =id_end_date
            p.Days =days
            p.save()

        return HttpResponse(True)
    else:
        pass



def remove_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount=0.0
        shipping_amount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            tempamount=(p.quantity*p.product.selling_price*p.Days)
            amount+=tempamount
        data={
            'amount':amount,
            'totalamount':amount+shipping_amount
        }
        return JsonResponse(data)

def buy_now(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/buynow.html',{'totalitem':totalitem})

@login_required
def address(request):
    add=Customer.objects.filter(user=request.user)
    totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary','totalitem':totalitem})

@login_required
def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html',{'order_placed':op,'totalitem':totalitem})

def tractor(request,data=None):
    totalitem=0
    if data==None:
        tractors=Product.objects.filter(category='T')
    elif data=='Sonalika' or data=='Mahindra':
        tractors=Product.objects.filter(category='T').filter(brand=data)
    elif data=='below':
        tractors=Product.objects.filter(category='T').filter(selling_price__lt=10000)
    elif data=='above':
        tractors=Product.objects.filter(category='T').filter(selling_price__gt=10000)
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/tractor.html',{'tractors':tractors,'totalitem':totalitem})

def engine(request,data=None):
    totalitem=0
    if data==None:
        engines=Product.objects.filter(category='E')
    elif data=='Yamaha' or data=='suzuki':
        engines=Product.objects.filter(category='E').filter(brand=data)
    elif data=='below':
        engines=Product.objects.filter(category='E').filter(selling_price__lt=10000)
    elif data=='above':
        engines=Product.objects.filter(category='E').filter(selling_price__gt=10000)
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/engine.html',{'engines':engines,'totalitem':totalitem})

def gardeningtool(request,data=None):
    totalitem=0
    if data==None:
        gardeningtools=Product.objects.filter(category='GT').filter(brand=data)
    elif data=='below':
        gardeningtools=Product.objects.filter(category='GT').filter(selling_price__lt=1000)
    elif data=='above':
        gardeningtools=Product.objects.filter(category='GT').filter(selling_price__gt=1000)
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/gardeningtool.html',{'gardeningtools':gardeningtools,'totalitem':totalitem})

def farmingtool(request,data=None):
    totalitem=0
    if data==None:
        farmingtools=Product.objects.filter(category='FT')
    elif data=='Lee' or data=='Spykar':
        farmingtools=Product.objects.filter(category='FT').filter(brand=data)
    elif data=='below':
        farmingtools=Product.objects.filter(category='FT').filter(selling_price__lt=1000)
    elif data=='above':
        farmingtools=Product.objects.filter(category='FT').filter(selling_price__gt=1000)
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/farmingtool.html',{'farmingtools':farmingtools,'totalitem':totalitem})

class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})
    
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html',{'form':form})
        
@login_required
def checkout(request):
    user=request.user
    add=Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.0
    totalamount=0.0
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity*p.product.selling_price*p.Days)
            amount+=tempamount
        totalamount=amount+shipping_amount
    totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/checkout.html',{'add':add,'totalamount':totalamount,'cart_items':cart_items,'totalitem':totalitem, 'amount':amount})

@login_required
def payment_done(request):
    if request.method == "GET":
        user = request.user
        custid = request.GET.get('custid')
        customer = Customer.objects.get(id=custid)
        cart = Cart.objects.filter(user=user)

        ord_id = []
        amount = 0.0
        shipping_amount = 70.0
        for c in cart:
            print("hello")
            print(c.product)
            save_ord = OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, Days=c.Days,
                                   Start_date=c.Start_date[0:10], End_date=c.End_date[0:10])
            save_ord.save()
            tempamount = (c.quantity * c.product.selling_price * c.Days)
            amount += tempamount

            ord_id.append(save_ord.id)
            c.delete()
        totalamount = amount + shipping_amount
        ids_od = OrderPlaced.objects.filter(id__in=ord_id)

        context = {'ids_od': ids_od, 'totalamount': totalamount, 'amount': amount}
        return render(request, "app/payment_page.html", context)
    else:
        money_amount_and_type = request.POST.get('money_amount')
        x = money_amount_and_type.split(",")

        money_amount=None
        tkn=None

        len = 0
        for i in x:
            len = len + 1
            if len == 1:
                money_amount = i
            else:
                tkn = i

        print(money_amount, tkn)

        try:
            customer = stripe.Customer.create(
                email=request.user.email,
                description=request.user.username,
                source=tkn
            )
            amount = float(money_amount)
            amount2 = int(amount)
            print(amount2)

            charge = stripe.Charge.create(
                amount=(amount2 * 100),
                currency="inr",
                customer=customer,
                description="Payment for Ecommerce",
            )

            messages.success(request, 'Your Payment Successful !')
            return redirect('orders')

        except stripe.error.CardError as e:
            messages.info(request, f"{e.error.message}")
            return redirect('home')

        except stripe.error.RateLimitError as e:
            messages.info(request, f"{e.error.message}")
            return redirect('home')
        except stripe.error.InvalidRequestError as e:
            messages.info(request, "Invalid Request !")
            return redirect('home')
        except stripe.error.AuthenticationError as e:
            messages.info(request, "Authentication Error !!")
            return redirect('home')
        except stripe.error.APIConnectionError as e:
            messages.info(request, "Check Your Connection !")
            return redirect('home')
        except stripe.error.StripeError as e:
            messages.info(request, "There was an error please try again !")
            return redirect('home')
        except Exception as e:
            messages.info(request, "A serious error occured we were notified !")
            return redirect('home')




@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})
    
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulations!! Profile Updated Successfully')
            totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})