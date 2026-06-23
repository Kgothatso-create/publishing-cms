from django.core.exceptions import ValidationError
from django.db import transaction

from people.models import (
    PersonIdentityDocument,
    PersonProfile,
    User,
)


class OnboardingService:
    """
    Service responsible for orchestrating onboarding operations.

    Responsibilities:
    - Transaction management
    - User persistence
    - Profile persistence
    - Document persistence
    - Onboarding status transitions
    """

    @classmethod
    @transaction.atomic
    def save(cls, user_form, profile_form, document_formset):
        """
        Create or update onboarding data.

        Expects already validated forms.

        Returns:
            User
        """

        user = user_form.save()

        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()

        cls._save_documents(
            user=user,
            document_formset=document_formset,
        )

        user.onboarding_status = cls._determine_status(
            user=user,
            profile=profile,
        )
        user.save(update_fields=["onboarding_status"])

        return user

    @classmethod
    @transaction.atomic
    def complete_onboarding(cls, user):
        """
        Explicit onboarding completion action.
        """

        if not cls._can_complete(user):
            raise ValidationError(
                "Onboarding requirements have not been met."
            )

        user.onboarding_status = User.OnboardingStatus.COMPLETED
        user.save(update_fields=["onboarding_status"])

        return user

    @classmethod
    def _save_documents(cls, user, document_formset):
        """
        Persist document formset changes.
        """

        documents = document_formset.save(commit=False)

        for document in documents:
            document.user = user
            document.save()

        for document in document_formset.deleted_objects:
            document.delete()

        if hasattr(document_formset, "save_m2m"):
            document_formset.save_m2m()

    @classmethod
    def _determine_status(cls, user, profile):
        """
        Determine onboarding status after save.
        """

        if cls._is_profile_complete(user, profile):
            return User.OnboardingStatus.IN_PROGRESS

        return User.OnboardingStatus.NOT_STARTED

    @classmethod
    def _is_profile_complete(cls, user, profile):
        """
        Required fields for IN_PROGRESS.
        """

        user_fields_complete = all(
            [
                user.first_name,
                user.last_name,
                user.email,
            ]
        )

        profile_fields_complete = all(
            [
                profile.gender,
                profile.race,
                profile.address_line_1,
                profile.city,
                profile.province,
                profile.postal_code,
                profile.country,
            ]
        )

        return user_fields_complete and profile_fields_complete

    @classmethod
    def _can_complete(cls, user):
        """
        Validation required before COMPLETED.
        """

        try:
            profile = user.personprofile
        except PersonProfile.DoesNotExist:
            return False

        return cls._is_profile_complete(
            user=user,
            profile=profile,
        )