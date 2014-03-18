
#include "transaction_data.h"
#include "nuodb_common.h"

int execute_delivery(struct db_context_t *dbc, struct delivery_t *data)
{
    char stmt[128];
    struct sql_result_t result;

    /* Create the query and execute it. */
    sprintf(stmt, "EXECUTE delivery(%d, %d)",
            data->w_id, data->o_carrier_id);
    if (!dbt2_sql_execute(dbc, stmt, &result, "DELIVERY"))
    {
        return ERROR;
    }

    return OK;
}
