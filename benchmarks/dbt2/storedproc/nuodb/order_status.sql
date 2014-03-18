drop procedure order_status if exists;

delimiter ~

CREATE PROCEDURE order_status (in_c_id INT,
         	               in_c_w_id INT,
	                       in_c_d_id INT,
	                       in_c_last TEXT)
RETURNS `order`(c_id INT, c_first VARCHAR(255), c_middle VARCHAR(255), c_last VARCHAR(255), c_balance NUMERIC(24,12),
              o_id INT, o_carrier_id INT, o_entry_d TIMESTAMP, o_ol_cnt INT, 
              ol_i_id INT, ol_supply_w_id INT, ol_quantity REAL, ol_amount REAL, ol_delivery_d TIMESTAMP)
AS
	VAR out_c_id, out_c_first, out_c_middle, out_c_last, out_c_balance;
        VAR out_o_id, out_o_carrier_id, out_o_entry_d, out_o_ol_cnt;

	/*
	 * Pick a customer by searching for c_last, should pick the one in the
	 * middle, not the first one.
	 */
	IF (in_c_id = 0 )
		out_c_id = (SELECT c_id
		           FROM customer
		           WHERE c_w_id = in_c_w_id
		             AND c_d_id = in_c_d_id
		             AND c_last = in_c_last
		           ORDER BY c_first ASC limit 1);
	ELSE
		out_c_id = in_c_id;
	END_IF;

	out_c_first, out_c_middle, out_c_last, out_c_balance = (SELECT c_first, c_middle, c_last, c_balance
	                                                       FROM customer
	                                                       WHERE c_w_id = in_c_w_id   
	                                                         AND c_d_id = in_c_d_id
	                                                         AND c_id = out_c_id);

	out_o_id, out_o_carrier_id, out_o_entry_d, out_o_ol_cnt = (SELECT o_id, o_carrier_id, o_entry_d, o_ol_cnt
	                                                          FROM orders
	                                                          WHERE o_w_id = in_c_w_id
  	                                                          AND o_d_id = in_c_d_id
  	                                                          AND o_c_id = out_c_id
	                                                          ORDER BY o_id DESC limit 1);

        FOR SELECT ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_delivery_d
            FROM order_line
            WHERE ol_w_id = in_c_w_id
                  AND ol_d_id = in_c_d_id
                  AND ol_o_id = out_o_id;

            INSERT INTO `order` VALUES(out_c_id, out_c_first, out_c_middle, out_c_last, out_c_balance,
                                     out_o_id, out_o_carrier_id, out_o_entry_d, out_o_ol_cnt,
                                     ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_delivery_d);
        END_FOR;

END_PROCEDURE~

delimiter ;
