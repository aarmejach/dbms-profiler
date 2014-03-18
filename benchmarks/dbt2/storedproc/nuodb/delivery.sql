drop procedure delivery if exists;

delimiter ~

CREATE PROCEDURE delivery(in_w_id INT, in_o_carrier_id INT)
AS

   VAR  out_c_id ;
   VAR  out_ol_amount ;
   VAR 	tmp_d_id = 1;
   VAR 	tmp_o_id = 0;

   while (tmp_d_id <= 10 )

     tmp_o_id = (SELECT no_o_id
                FROM new_order
                WHERE no_w_id = in_w_id AND no_d_id = tmp_d_id limit 1);

     IF (tmp_o_id > 0) 
       DELETE FROM new_order 
       WHERE no_o_id = tmp_o_id 
         AND no_w_id = in_w_id 
         AND no_d_id = tmp_d_id;
 
       out_c_id = (SELECT o_c_id
                  FROM orders
                  WHERE o_id = tmp_o_id
                    AND o_w_id = in_w_id
                    AND o_d_id = tmp_d_id);
 
       UPDATE orders
       SET o_carrier_id = in_o_carrier_id
       WHERE o_id = tmp_o_id
         AND o_w_id = in_w_id
         AND o_d_id = tmp_d_id;
 
       UPDATE order_line
       SET ol_delivery_d = now()
       WHERE ol_o_id = tmp_o_id
         AND ol_w_id = in_w_id
         AND ol_d_id = tmp_d_id;
 
       out_ol_amount = (SELECT SUM(ol_amount * ol_quantity)
                       FROM order_line
                       WHERE ol_o_id = tmp_o_id
                         AND ol_w_id = in_w_id
                         AND ol_d_id = tmp_d_id);
 
       UPDATE customer
       SET c_delivery_cnt = c_delivery_cnt + 1,
           c_balance = c_balance + out_ol_amount
       WHERE c_id = out_c_id
         AND c_w_id = in_w_id
         AND c_d_id = tmp_d_id;

     END_IF;

     tmp_d_id = tmp_d_id + 1;

   END_WHILE;
END_PROCEDURE~

delimiter ;


