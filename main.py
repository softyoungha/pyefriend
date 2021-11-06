
from pyefriend import DomesticApi, domestic_context


def main(test: bool = False):
    with domestic_context(test=test) as session:
        session: DomesticApi
        print('session.is_connected', session.is_connected)
        print('isVTS', session.conn.IsVTS())
        print('encrypted_password', session.encrypted_password)
        print('all_accounts', session.all_accounts)
        print('Session', session.conn.GetAccountCount())

        # 신세계 코드
        product_code = '004170'
        print('명칭', session.get_stock_name(product_code))
        print('신세계 가격', session.get_stock_price(product_code))
        print(session.buy_stock('004170', 1))
        print('get_total_cash', session.get_total_cash())
        print('get_stocks', session.get_stocks())
        print('get_processed_orders', session.get_processed_orders('20211001'))
        print('get_unprocessed_orders', session.get_unprocessed_orders())

if __name__ == "__main__":
    main()
