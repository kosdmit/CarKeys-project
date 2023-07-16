from app_ecommerce.forms import CustomerForm
from app_ecommerce.models import Customer


class AddCallbackFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session_id = self.request.session.session_key
        if session_id:
            customer = Customer.objects.filter(session_id=session_id).first()
        else:
            self.request.session.create()
            session_id = self.request.session.session_key
            customer = Customer.objects.create(session_id=session_id)

        customer_form = CustomerForm(instance=customer)
        context['customer_form'] = customer_form

        return context