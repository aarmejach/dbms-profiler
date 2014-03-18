drop procedure stock_level if exists;

delimiter ~

CREATE PROCEDURE stock_level(in_w_id INT,
                             in_d_id INT,
                             in_threshold INT,
                             OUT low_stock INT)
AS

  VAR tmp_d_next_o_id  = (SELECT d_next_o_id
                         FROM district
                         WHERE d_w_id = in_w_id
                           AND d_id = in_d_id);

  low_stock = (SELECT count(*)
              FROM order_line, stock, district
              WHERE d_id = in_d_id
                    AND d_w_id = in_w_id
                    AND d_id = ol_d_id
                    AND d_w_id = ol_w_id
                    AND ol_i_id = s_i_id
                    AND ol_w_id = s_w_id
                    AND s_quantity < in_threshold
                    AND ol_o_id BETWEEN (tmp_d_next_o_id - 20)
                                    AND (tmp_d_next_o_id - 1));

END_PROCEDURE~

delimiter ;

