/*
 * This file is released under the terms of the Artistic License.  Please see
 * the file LICENSE, included in this package, for details.
 *
 * Copyright (C) 2002 Mark Wong & Open Source Development Labs, Inc.
 * Copyright (C) 2004 Alexey Stroganov & MySQL AB.
 *
 */

#include <nonsp_new_order.h>

/* Probably should move these into a nuodb_new_order.h */

#define NUODB_NEW_ORDER \
        "EXECUTE new_order(%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)"

const char s_dist[10][11] = {
    "s_dist_01", "s_dist_02", "s_dist_03", "s_dist_04", "s_dist_05",
    "s_dist_06", "s_dist_07", "s_dist_08", "s_dist_09", "s_dist_10"
};

int execute_new_order(struct db_context_t *dbc, struct new_order_t *data)
{
    int rc;

    char * vals[6];
    int nvals=6;

    rc= new_order(dbc, data, vals, nvals);

    if (rc)
    {
        LOG_ERROR_MESSAGE("NEW_ORDER FINISHED WITH RC %d\n", rc);

        //should free memory that was allocated for nvals vars
        dbt2_free_values(vals, nvals);

        return ERROR;
    }

    return OK;
}

int  new_order(struct db_context_t *dbc, struct new_order_t *data, char ** vals, int nvals)
{
    /* Input variables. */
    int w_id = data->w_id;
    int d_id = data->d_id;
    int c_id = data->c_id;
    int o_all_local = data->o_all_local;
    int o_ol_cnt = data->o_ol_cnt;

    int ol_i_id[15];
    int ol_supply_w_id[15];
    int ol_quantity[15];

    char query[1024];
    struct sql_result_t result;
    int i;

    /* Loop through the last set of parameters. */
    for (i = 0; i < 15; i++) {
        ol_i_id[i] = data->order_line[i].ol_i_id;
        ol_supply_w_id[i] = data->order_line[i].ol_supply_w_id;
        ol_quantity[i] = data->order_line[i].ol_quantity;
    }

    sprintf(query, NUODB_NEW_ORDER, w_id, d_id, c_id, o_all_local, o_ol_cnt,
            ol_i_id[0], ol_supply_w_id[0], ol_quantity[0],
            ol_i_id[1], ol_supply_w_id[1], ol_quantity[1],
            ol_i_id[2], ol_supply_w_id[2], ol_quantity[2],
            ol_i_id[3], ol_supply_w_id[3], ol_quantity[3],
            ol_i_id[4], ol_supply_w_id[4], ol_quantity[4],
            ol_i_id[5], ol_supply_w_id[5], ol_quantity[5],
            ol_i_id[6], ol_supply_w_id[6], ol_quantity[6],
            ol_i_id[7], ol_supply_w_id[7], ol_quantity[7],
            ol_i_id[8], ol_supply_w_id[8], ol_quantity[8],
            ol_i_id[9], ol_supply_w_id[9], ol_quantity[9],
            ol_i_id[10], ol_supply_w_id[10], ol_quantity[10],
            ol_i_id[11], ol_supply_w_id[11], ol_quantity[11],
            ol_i_id[12], ol_supply_w_id[12], ol_quantity[12],
            ol_i_id[13], ol_supply_w_id[13], ol_quantity[13],
            ol_i_id[14], ol_supply_w_id[14], ol_quantity[14]);

#ifdef DEBUG_QUERY
    LOG_ERROR_MESSAGE("NEW_ORDER_1: %s\n",query);
#endif
    if (!dbt2_sql_execute(dbc, query, &result, "NEW_ORDER"))
    {
        return 10;
    }

    return 0;
}

