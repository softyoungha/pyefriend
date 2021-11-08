
from pyefriend import DomesticApi, domestic_context


def main():
    with domestic_context() as api:
        api: DomesticApi
        print('session.is_connected', api.is_connected)
        print('isVTS', api.conn.IsVTS())
        print('encrypted_password', api.encrypted_password)
        print('all_accounts', api.all_accounts)
        print('Session', api.conn.GetAccountCount())

        # 신세계 코드
        product_code = '004170'
        print('명칭', api.get_stock_name(product_code))
        print('신세계 가격', api.get_stock_info(product_code))
        print(api.buy_stock('004170', 1))
        print('get_total_cash', api.get_total_cash())
        print('get_stocks', api.get_stocks())
        print('get_processed_orders', api.get_processed_orders('20211001'))
        print('get_unprocessed_orders', api.get_unprocessed_orders())

if __name__ == "__main__":
    main()
