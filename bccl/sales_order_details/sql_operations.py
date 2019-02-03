import pymysql

def insert_data(conn, data):
    
    collieries_data = data['colliery_data']

    with conn.cursor() as cur:
        for colliery_data in collieries_data:
            insert_query = '''INSERT INTO bccl_sales_order_details 
                            (colliery_name, colliery_id, area_name, area_id, `Scheme(FSA/Auction etc)`, `Grade&Size(Product Description)`,`Consignee ID`, `Consignee Name`, `Sales Order No.`, `Sales Order Date`, `Sales Order Expiry Date`, `Sales Order Quantity`)
                            VALUES (
                                "{colliery_name}", "{colliery_id}",  "{area_name}", "{area_id}", "{scheme}", "{product_description}", "{consignee_id}", "{consignee_name}", "{sales_order_no}", DATE_FORMAT(STR_TO_DATE("{order_date}", '%d-%m-%Y'), '%Y-%m-%d'), 
                                DATE_FORMAT(STR_TO_DATE("{expiry_date}", '%d-%m-%Y'), '%Y-%m-%d'), "{order_qty}"
                            )
                            '''.format(
                                        colliery_name = data["colliery_name"], 
                                        colliery_id = data["colliery_id"], 
                                        area_name = data["area_name"], 
                                        area_id = data["area_id"], 
                                        scheme = colliery_data["Scheme(FSA/Auction etc)"],
                                        product_description = colliery_data["Grade&Size(Product Description)"],
                                        consignee_id = colliery_data["Consignee ID"],
                                        consignee_name = colliery_data["Consignee Name"],
                                        sales_order_no = colliery_data["Sales Order No."],
                                        order_date = colliery_data["Sales Order Date"],
                                        expiry_date = colliery_data["Sales Order Expiry Date"],
                                        order_qty = colliery_data["Sales Order Quantity"]
                                )
            print(insert_query)
            success = cur.execute(insert_query)
            print(success)
            conn.commit()



