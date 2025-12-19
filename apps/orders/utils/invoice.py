from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse


def generate_invoice_pdf(order):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{order.order_number}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, "JioMart Invoice")

    y -= 30
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Order Number: {order.order_number}")
    y -= 20
    p.drawString(50, y, f"Order Date: {order.created_at.strftime('%d %b %Y')}")
    y -= 20
    p.drawString(50, y, f"Customer: {order.customer.name}")

    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Items")
    y -= 20

    p.setFont("Helvetica", 11)

    for item in order.items.all():
        p.drawString(50, y, item.product.name)
        p.drawString(300, y, f"{item.quantity} x ₹{item.price}")
        p.drawString(450, y, f"₹{item.subtotal}")
        y -= 20

        if y < 100:
            p.showPage()
            y = height - 50

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y, "Total:")
    p.drawString(450, y, f"₹{order.total_amount}")

    p.showPage()
    p.save()

    return response
