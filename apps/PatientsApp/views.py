from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.AccountsApp.models import User

from .models import Patient


@login_required
def patient_list(request):
    patients = Patient.objects.select_related('user').order_by(
        'user__last_name',
        'user__first_name',
    )

    return render(
        request,
        'PatientsApp/list.html',
        {'patients': patients},
    )


@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(
        Patient.objects.select_related('user'),
        id=patient_id,
    )

    return render(
        request,
        'PatientsApp/detail.html',
        {'patient': patient},
    )


@login_required
def patient_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        date_of_birth = request.POST.get('date_of_birth', '')
        sex = request.POST.get('sex', '')
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        emergency_contact_name = request.POST.get(
            'emergency_contact_name',
            '',
        ).strip()
        emergency_contact_phone = request.POST.get(
            'emergency_contact_phone',
            '',
        ).strip()

        if not username:
            messages.error(request, 'Username is required.')
        elif not date_of_birth:
            messages.error(request, 'Date of birth is required.')
        elif sex not in Patient.Sex.values:
            messages.error(request, 'Select a valid sex.')
        elif Patient.objects.filter(user__username=username).exists():
            messages.error(
                request,
                'That user already has a patient profile.',
            )
        else:
            user = User.objects.filter(
                username=username,
                role=User.Role.PATIENT,
            ).first()

            if user is None:
                messages.error(
                    request,
                    'A valid patient user is required.',
                )
            else:
                Patient.objects.create(
                    user=user,
                    date_of_birth=date_of_birth,
                    sex=sex,
                    phone_number=phone_number,
                    address=address,
                    emergency_contact_name=emergency_contact_name,
                    emergency_contact_phone=emergency_contact_phone,
                )

                patient = Patient.objects.get(user=user)

                messages.success(
                    request,
                    'Patient profile created successfully.',
                )

                return redirect(
                    'PatientsApp:detail',
                    patient_id=patient.id,
                )

    users = User.objects.filter(
        patient_profile__isnull=True,
        role=User.Role.PATIENT,
    ).order_by('username')

    return render(
        request,
        'PatientsApp/create.html',
        {'users': users},
    )


@login_required
def patient_edit(request, patient_id):
    patient = get_object_or_404(
        Patient.objects.select_related('user'),
        id=patient_id,
    )

    if request.method == 'POST':
        date_of_birth = request.POST.get('date_of_birth', '')
        sex = request.POST.get('sex', '')
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        emergency_contact_name = request.POST.get(
            'emergency_contact_name',
            '',
        ).strip()
        emergency_contact_phone = request.POST.get(
            'emergency_contact_phone',
            '',
        ).strip()

        if not date_of_birth:
            messages.error(request, 'Date of birth is required.')
        elif sex not in Patient.Sex.values:
            messages.error(request, 'Select a valid sex.')
        else:
            patient.date_of_birth = date_of_birth
            patient.sex = sex
            patient.phone_number = phone_number
            patient.address = address
            patient.emergency_contact_name = emergency_contact_name
            patient.emergency_contact_phone = emergency_contact_phone
            patient.save()

            messages.success(
                request,
                'Patient profile updated successfully.',
            )

            return redirect(
                'PatientsApp:detail',
                patient_id=patient.id,
            )

    return render(
        request,
        'PatientsApp/edit.html',
        {
            'patient': patient,
            'sex_choices': Patient.Sex.choices,
        },
    )


@login_required
def patient_timeline(request, patient_id):
    patient = get_object_or_404(
        Patient.objects.select_related('user'),
        id=patient_id,
    )

    return render(
        request,
        'PatientsApp/timeline.html',
        {'patient': patient},
    )