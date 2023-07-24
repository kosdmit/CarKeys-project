from app_ecommerce.forms import CustomerForm, MessageForm
from app_ecommerce.models import Customer, Service


class AddCustomerFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer_form_data = self.request.session.pop('customer_form_data', None)
        if customer_form_data:
            customer_form = CustomerForm(customer_form_data)
        else:
            session_id = self.request.session.session_key
            customer = Customer.objects.filter(session_id=session_id).first()
            customer_form = CustomerForm(instance=customer)

        context['customer_form'] = customer_form
        context['message_form'] = MessageForm()

        return context


class AddPriceListDataMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        price_list = Service.objects.all()
        context['price_list'] = price_list

        return context