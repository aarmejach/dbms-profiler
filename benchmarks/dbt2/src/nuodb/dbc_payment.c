/*
 * This file is released under the terms of the Artistic License.  Please see
 * the file LICENSE, included in this package, for details.
 *
 */

#include "transaction_data.h"
#include "nuodb_common.h"

int execute_payment(struct db_context_t *dbc, struct payment_t *data)
{
    char stmt[128];
    struct sql_result_t result;

    /* Create the query and execute it. */
    sprintf(stmt, "EXECUTE payment(%d, %d, %d, %d, %d, '%s', %f)",
            data->w_id, data->d_id, data->c_id, data->c_w_id, data->c_d_id,
            data->c_last, data->h_amount);
    if (!dbt2_sql_execute(dbc, stmt, &result, "PAYMENT"))
    {
        return ERROR;
    }

    return OK;
}
