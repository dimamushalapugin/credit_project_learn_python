from webapp.payment.models import Seller


def check_seller_in_base(seller_inn):
    new_seller = Seller.query.filter(
        Seller.seller_inn == seller_inn).first()
    print(new_seller)
    if new_seller:
        return 'Да'
    return 'Нет'
