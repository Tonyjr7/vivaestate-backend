from django.db.models.signals import post_save
from django.dispatch import receiver
from social.models import Favourite
from services import send_whatsapp_message

@receiver(post_save, sender=Favourite)
def send_intrest_and_lead_notification(sender, instance, created, **kwargs):
    """
    Notify the assigned agent about user intrested in their property
    and user about the assigned agent """

    if created:
        agent=instance.assigned_agent
        if agent and agent.whatsapp_number:
            agent_message = (
                f"📢 New Prospect Assignment!\n\n"
                f"🔹 **Prospect Buyer**: {instance.user.first_name}\n"
                f"📞 Contact: {instance.user.whatsapp_number}\n"
                f"🏡 Interested in: {instance.property}\n\n"
                f"Please follow up with the buyer."
            )
            send_whatsapp_message(agent.whatsapp_number, agent_message)
        prospect_buyer_whatsapp_no = instance.user.whatsapp_number
        if prospect_buyer_whatsapp_no:
            buyer_message = (
                f"Hello {instance.user.first_name}, 👋\n\n"
                f"We see you're interested in **{instance.property}**! 🏡\n\n"
                f"📞 You can contact our assigned agent: {agent.first_name} at {agent.whatsapp_number}.\n\n"
                f"Thanks for using our platform! 🚀"
            )
            send_whatsapp_message(prospect_buyer_whatsapp_no, buyer_message)
 