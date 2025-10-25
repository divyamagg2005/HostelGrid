from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Fee
from .forms import FeeForm, FeeUpdateForm
from students.models import Student


def is_admin(user):
    """Check if user is admin"""
    if user.is_superuser:
        return True
    try:
        return user.profile.role == 'admin'
    except:
        return False


@login_required
def payment_list(request):
    """List payments based on user role"""
    if is_admin(request.user):
        # Admin sees all payments
        payments = Fee.objects.all()
        template = 'payments/payment_list.html'
    else:
        # Student sees only their payments
        try:
            # Try to find student by username matching
            student = Student.objects.filter(name__icontains=request.user.username).first()
            if not student:
                # If no exact match, try to find by user profile or create a basic student record
                student = Student.objects.filter(studentid=request.user.id).first()
            
            if student:
                payments = Fee.objects.filter(studentid=student)
            else:
                payments = []
                messages.warning(request, 'Student profile not found.')
        except Exception as e:
            payments = []
            messages.warning(request, f'Error finding student profile: {str(e)}')
        template = 'payments/student_payment_list.html'
    
    context = {
        'payments': payments,
    }
    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def payment_add(request):
    """Add new payment (admin only)"""
    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            payment = form.save()
            
            # Create PaymentRecord if payment_type is provided
            payment_type = form.cleaned_data.get('payment_type')
            if payment_type:
                from .models import PaymentRecord
                PaymentRecord.objects.create(
                    fee=payment,
                    payment_type=payment_type
                )
            
            messages.success(request, f'Payment added for {payment.student.name}!')
            return redirect('payment_list')
    else:
        form = FeeForm()
    
    context = {
        'form': form,
        'title': 'Add Payment',
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_detail(request, pk):
    """View payment details"""
    payment = get_object_or_404(Fee, pk=pk)
    
    # Check permissions and determine template
    if is_admin(request.user):
        template = 'payments/payment_detail.html'
    else:
        try:
            # Try to find student by username matching
            student = Student.objects.filter(name__icontains=request.user.username).first()
            if not student:
                # If no exact match, try to find by user profile or create a basic student record
                student = Student.objects.filter(studentid=request.user.id).first()
            
            if not student:
                messages.error(request, 'Student profile not found.')
                return redirect('dashboard')
            
            if payment.studentid != student:
                messages.error(request, 'You do not have permission to view this payment.')
                return redirect('payment_list')
        except Exception as e:
            messages.error(request, f'Error finding student profile: {str(e)}')
            return redirect('dashboard')
        
        template = 'payments/student_payment_detail.html'
    
    context = {
        'payment': payment,
    }
    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def payment_edit(request, pk):
    """Edit payment (admin only)"""
    payment = get_object_or_404(Fee, pk=pk)
    
    if request.method == 'POST':
        form = FeeForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            
            # Update or create PaymentRecord if payment_type is provided
            payment_type = form.cleaned_data.get('payment_type')
            if payment_type:
                from .models import PaymentRecord
                PaymentRecord.objects.update_or_create(
                    fee=payment,
                    defaults={'payment_type': payment_type}
                )
            else:
                # If payment_type is empty, delete the PaymentRecord if it exists
                try:
                    payment_record = payment.payment_record
                    payment_record.delete()
                except:
                    pass
            
            messages.success(request, 'Payment updated successfully!')
            return redirect('payment_detail', pk=pk)
    else:
        form = FeeForm(instance=payment)
    
    context = {
        'form': form,
        'title': 'Edit Payment',
        'payment': payment,
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
@user_passes_test(is_admin)
def payment_update_status(request, pk):
    """Update payment status (admin only)"""
    payment = get_object_or_404(Fee, pk=pk)
    
    if request.method == 'POST':
        form = FeeUpdateForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            # Update status to Paid if marked as paid
            if payment.status == 'Paid':
                pass  # Fee model doesn't have payment_date field
            payment.save()
            messages.success(request, 'Payment status updated successfully!')
            return redirect('payment_detail', pk=pk)
    else:
        form = FeeUpdateForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'title': 'Update Payment Status',
    }
    return render(request, 'payments/payment_update.html', context)


@login_required
@user_passes_test(is_admin)
def payment_delete(request, pk):
    """Delete payment (admin only)"""
    payment = get_object_or_404(Fee, pk=pk)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('payment_list')
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_confirm_delete.html', context)


@login_required
def student_payment_make(request):
    """Student payment interface with dropdown and amount controls"""
    # Try to find student by username matching
    student = Student.objects.filter(name__icontains=request.user.username).first()
    if not student:
        # If no exact match, try to find by user profile or create a basic student record
        student = Student.objects.filter(studentid=request.user.id).first()
    
    if not student:
        messages.error(request, 'Student profile not found. Please contact admin.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        payment_type = request.POST.get('payment_type')
        amount = request.POST.get('amount')
        
        if payment_type and amount:
            try:
                # Create a new fee record for the student
                fee = Fee.objects.create(
                    studentid=student,
                    amount=amount,
                    duedate=timezone.now().date(),
                    status='Paid'  # Mark as paid since student is making payment
                )
                
                # Create a payment record to track the payment type
                from .models import PaymentRecord
                PaymentRecord.objects.create(
                    fee=fee,
                    payment_type=payment_type
                )
                
                messages.success(request, f'Payment of ₹{amount} for {payment_type} has been processed successfully!')
                return redirect('payment_list')
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'student': student,
    }
    return render(request, 'payments/student_payment_make.html', context)
