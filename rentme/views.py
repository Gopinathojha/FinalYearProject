from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import User, Property

def welcome(request):
    return render(request, 'rentme/welcome.html')

def customer_login_signup(request):
    if request.method == 'POST':
        if 'signup' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            name = request.POST['name']
            if password != confirm_password:
                return render(request, 'rentme/customer_login_signup.html', {'error': 'Passwords do not match'})
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=name,
                    is_customer=True
                )
                messages.success(request, 'Signup successful! Please log in.')
                return redirect('customer_login_signup')
            except IntegrityError:
                return render(request, 'rentme/customer_login_signup.html', {'error': 'Email already exists'})
            except Exception as e:
                return render(request, 'rentme/customer_login_signup.html', {'error': f'An error occurred: {str(e)}'})
        elif 'signin' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, username=email, password=password)
            if user and user.is_customer:
                login(request, user)
                return redirect('customer_landing')
            else:
                return render(request, 'rentme/customer_login_signup.html', {'error': 'Invalid credentials or not a customer'})
    return render(request, 'rentme/customer_login_signup.html')

def seller_login_signup(request):
    if request.method == 'POST':
        if 'signup' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            name = request.POST['name']
            mobile_number = request.POST['mobile_number']
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=name,
                    mobile_number=mobile_number,
                    is_seller=True
                )
                messages.success(request, 'Signup successful! Please log in.')
                return redirect('seller_login_signup')
            except IntegrityError:
                return render(request, 'rentme/seller_login_signup.html', {'error': 'Email already exists'})
            except Exception as e:
                return render(request, 'rentme/seller_login_signup.html', {'error': f'An error occurred: {str(e)}'})
        elif 'signin' in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, username=email, password=password)
            if user and user.is_seller:
                login(request, user)
                return redirect('seller_landing')
            else:
                return render(request, 'rentme/seller_login_signup.html', {'error': 'Invalid credentials or not a seller'})
    return render(request, 'rentme/seller_login_signup.html')

@login_required
def customer_landing(request):
    if not request.user.is_customer:
        return redirect('welcome')
    
    # Fetch the latest 8 properties ordered by creation date (newest first)
    properties = Property.objects.all().order_by('-created_at')[:8]
    
    return render(request, 'rentme/customer_landing.html', {
        'username': request.user.first_name,
        'properties': properties,
    })

@login_required
def all_properties(request):
    if not request.user.is_customer:
        return redirect('welcome')
    
    # Fetch all properties ordered by creation date (newest first)
    properties = Property.objects.all().order_by('-created_at')
    
    return render(request, 'rentme/all_properties.html', {
        'username': request.user.first_name,
        'properties': properties,
    })

@login_required
def property_detail(request, property_id):
    if not request.user.is_customer:
        messages.error(request, 'You must be a customer to view property details.')
        return redirect('welcome')
    
    try:
        # Fetch the property by ID
        property = get_object_or_404(Property, id=property_id)
        
        # Determine the property name based on type
        property_name = property.pg_name if property.property_type == 'pg' else property.room_title
        
        return render(request, 'rentme/property_detail.html', {
            'username': request.user.first_name,
            'property': property,
            'property_name': property_name,
        })
    except Exception as e:
        messages.error(request, f'Error fetching property details: {str(e)}')
        return redirect('all_properties')

@login_required
def seller_landing(request):
    if not request.user.is_seller:
        return redirect('welcome')
    
    if request.method == 'POST':
        print("=== Form Submission Started ===")
        print("POST Data:", request.POST)
        print("FILES:", request.FILES)

        property_type = request.POST.get('propertyType')
        if not property_type:
            messages.error(request, 'Property type is required.')
            return redirect('seller_landing')

        if property_type not in ['pg', 'room']:
            messages.error(request, 'Invalid property type.')
            return redirect('seller_landing')

        # Collect common fields
        property_data = {
            'seller': request.user,
            'property_type': property_type,
            'location': request.POST.get(f'{property_type}Location', '').strip(),
            'rent': request.POST.get(f'{property_type}Rent', ''),
            'availability': request.POST.get(f'{property_type}Availability', '').strip(),
            'details': request.POST.get(f'{property_type}Details', ''),
            'image1': request.FILES.get('image1'),
            'image2': request.FILES.get('image2'),
            'image3': request.FILES.get('image3'),
        }

        # Validate common required fields
        required_common_fields = ['location', 'rent', 'availability']
        missing_common_fields = [field for field in required_common_fields if not property_data[field]]
        if missing_common_fields:
            messages.error(request, f'Missing required fields: {", ".join(missing_common_fields)}')
            return redirect('seller_landing')

        # Validate rent as a number
        try:
            property_data['rent'] = float(property_data['rent'])
            if property_data['rent'] <= 0:
                messages.error(request, 'Rent must be a positive number.')
                return redirect('seller_landing')
        except (ValueError, TypeError):
            messages.error(request, 'Rent must be a valid number.')
            return redirect('seller_landing')

        # Validate images
        images = [property_data['image1'], property_data['image2'], property_data['image3']]
        images = [img for img in images if img]
        if len(images) < 2:
            messages.error(request, 'Please upload at least 2 images.')
            return redirect('seller_landing')

        # Handle PG-specific fields
        if property_type == 'pg':
            required_pg_fields = ['pgName', 'pgRoomType', 'pgCapacity']
            pg_fields = {
                'pg_name': request.POST.get('pgName', '').strip(),
                'pg_room_type': request.POST.get('pgRoomType', ''),
                'pg_capacity': request.POST.get('pgCapacity', ''),
                'pg_wifi': 'pgWifi' in request.POST,
                'pg_meals': 'pgMeals' in request.POST,
                'pg_ac': 'pgAC' in request.POST,
                'pg_laundry': 'pgLaundry' in request.POST,
                'pg_security': 'pgSecurity' in request.POST,
                'pg_power': 'pgPower' in request.POST,
                'pg_parking': 'pgParking' in request.POST,
                'pg_meal_type': request.POST.get('pgMealType', ''),
                'pg_tenants': request.POST.get('pgTenants', ''),
            }
            missing_pg_fields = [field for field in required_pg_fields if not request.POST.get(field, '').strip()]
            if missing_pg_fields:
                messages.error(request, f'Missing required PG fields: {", ".join(missing_pg_fields)}')
                return redirect('seller_landing')

            try:
                pg_fields['pg_capacity'] = int(pg_fields['pg_capacity']) if pg_fields['pg_capacity'] else None
                if pg_fields['pg_capacity'] is not None and pg_fields['pg_capacity'] <= 0:
                    messages.error(request, 'PG capacity must be a positive number.')
                    return redirect('seller_landing')
            except (ValueError, TypeError):
                messages.error(request, 'PG capacity must be a valid number.')
                return redirect('seller_landing')

            property_data.update(pg_fields)
        elif property_type == 'room':
            required_room_fields = ['roomTitle', 'roomSize', 'roomFloor', 'roomBathroomType']
            room_fields = {
                'room_title': request.POST.get('roomTitle', '').strip(),
                'room_size': request.POST.get('roomSize', '').strip(),
                'room_floor': request.POST.get('roomFloor', ''),
                'room_bathroom': 'roomBathroom' in request.POST,
                'room_balcony': 'roomBalcony' in request.POST,
                'room_furnished': 'roomFurnished' in request.POST,
                'room_kitchen': 'roomKitchen' in request.POST,
                'room_light': 'roomLight' in request.POST,
                'room_wardrobe': 'roomWardrobe' in request.POST,
                'room_parking': 'roomParking' in request.POST,
                'room_bathroom_type': request.POST.get('roomBathroomType', ''),
                'room_tenants': request.POST.get('roomTenants', ''),
            }
            missing_room_fields = [field for field in required_room_fields if not request.POST.get(field, '').strip()]
            if missing_room_fields:
                messages.error(request, f'Missing required Room fields: {", ".join(missing_room_fields)}')
                return redirect('seller_landing')

            try:
                room_fields['room_floor'] = int(room_fields['room_floor']) if room_fields['room_floor'] else None
                if room_fields['room_floor'] is not None and room_fields['room_floor'] < 0:
                    messages.error(request, 'Room floor must be a non-negative number.')
                    return redirect('seller_landing')
            except (ValueError, TypeError):
                messages.error(request, 'Room floor must be a valid number.')
                return redirect('seller_landing')

            property_data.update(room_fields)

        try:
            print("Attempting to save property with data:", property_data)
            property = Property.objects.create(**property_data)
            print("Property saved successfully:", property)
            messages.success(request, 'Property added successfully!')
        except Exception as e:
            print("Error saving property:", str(e))
            messages.error(request, f'Error adding property: {str(e)}')
        return redirect('seller_landing')

    properties = Property.objects.filter(seller=request.user).order_by('-created_at')
    print("Properties retrieved:", list(properties))
    return render(request, 'rentme/seller_landing.html', {
        'username': request.user.first_name,
        'properties': properties,
    })

@login_required
def delete_property(request, property_id):
    if not request.user.is_seller:
        return redirect('welcome')
    property = get_object_or_404(Property, id=property_id, seller=request.user)
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'Property deleted successfully!')
        return redirect('seller_landing')
    return redirect('seller_landing')

def user_logout(request):
    logout(request)
    return redirect('welcome')

def privacy_policy(request):
    return render(request, 'rentme/privacy.html')