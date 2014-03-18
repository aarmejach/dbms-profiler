
#include "transaction_data.h"
#include "nuodb_common.h"

int execute_order_status(struct db_context_t *dbc, struct order_status_t *data)
{
    char stmt[512];
    struct sql_result_t result;

    /* Create the query and execute it. */
    sprintf(stmt, "EXECUTE order_status(%d, %d, %d, '%s')",
            data->c_id, data->c_w_id, data->c_d_id, data->c_last);
    if(!dbt2_sql_execute(dbc, stmt, &result, "ORDER_STATUS"))
    {
        return ERROR;
    }

    return OK;
}
