from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Complaint
from .forms import ComplaintForm, ComplaintUpdateForm
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
def complaint_list(request):
    """List complaints based on user role"""
    if is_admin(request.user):
        # Admin sees all complaints
        complaints = Complaint.objects.all()
        template = 'complaints/complaint_list.html'
    else:
        # Student sees only their complaints
        try:
            # Try to find student by username matching
            student = Student.objects.filter(name__icontains=request.user.username).first()
            if not student:
                # If no exact match, try to find by user profile or create a basic student record
                student = Student.objects.filter(studentid=request.user.id).first()
            
            if student:
                complaints = Complaint.objects.filter(student=student)
            else:
                complaints = []
                messages.warning(request, 'Student profile not found.')
        except Exception as e:
            complaints = []
            messages.warning(request, f'Error finding student profile: {str(e)}')
        template = 'complaints/student_complaint_list.html'
    
    context = {
        'complaints': complaints,
    }
    return render(request, template, context)


@login_required
def complaint_add(request):
    """Add new complaint (students only)"""
    # Try to find student by username matching
    student = Student.objects.filter(name__icontains=request.user.username).first()
    if not student:
        # If no exact match, try to find by user profile or create a basic student record
        student = Student.objects.filter(studentid=request.user.id).first()
    
    if not student:
        messages.error(request, 'Student profile not found. Please contact admin.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = student
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('complaint_list')
    else:
        form = ComplaintForm()
    
    # Determine template based on user role
    if is_admin(request.user):
        template = 'complaints/complaint_form.html'
    else:
        template = 'complaints/student_complaint_form.html'
    
    context = {
        'form': form,
        'title': 'Submit Complaint',
    }
    return render(request, template, context)


@login_required
def complaint_detail(request, pk):
    """View complaint details"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check permissions and determine template
    if is_admin(request.user):
        template = 'complaints/complaint_detail.html'
    else:
        # Try to find student by username matching
        student = Student.objects.filter(name__icontains=request.user.username).first()
        if not student:
            # If no exact match, try to find by user profile or create a basic student record
            student = Student.objects.filter(studentid=request.user.id).first()
        
        if not student:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
        
        if complaint.student != student:
            messages.error(request, 'You do not have permission to view this complaint.')
            return redirect('complaint_list')
        
        template = 'complaints/student_complaint_detail.html'
    
    context = {
        'complaint': complaint,
    }
    return render(request, template, context)


@login_required
@user_passes_test(is_admin)
def complaint_update(request, pk):
    """Update complaint status (admin only)"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            if complaint.status == 'resolved' and not complaint.resolved_at:
                complaint.resolved_at = timezone.now()
            complaint.save()
            messages.success(request, 'Complaint updated successfully!')
            return redirect('complaint_detail', pk=pk)
    else:
        form = ComplaintUpdateForm(instance=complaint)
    
    context = {
        'form': form,
        'complaint': complaint,
        'title': 'Update Complaint',
    }
    return render(request, 'complaints/complaint_update.html', context)


@login_required
@user_passes_test(is_admin)
def complaint_resolve(request, pk):
    """Mark complaint as resolved and delete it (admin only)"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        student_name = complaint.student.name
        complaint.delete()
        messages.success(request, f'Complaint from {student_name} marked as resolved and removed!')
        return redirect('complaint_list')
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/complaint_confirm_resolve.html', context)


@login_required
def complaint_delete(request, pk):
    """Delete complaint (students can delete their own, admins can delete any)"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check permissions
    if not is_admin(request.user):
        # Students can only delete their own complaints
        student = Student.objects.filter(name__icontains=request.user.username).first()
        if not student:
            student = Student.objects.filter(studentid=request.user.id).first()
        
        if not student or complaint.student != student:
            messages.error(request, 'You do not have permission to delete this complaint.')
            return redirect('complaint_list')
    
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Complaint deleted successfully!')
        return redirect('complaint_list')
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/complaint_confirm_delete.html', context)
