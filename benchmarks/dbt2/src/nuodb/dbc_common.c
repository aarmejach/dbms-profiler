#include <stdlib.h>
#include <string.h>
#include "common.h"
#include "logging.h"
#include "nuodb_common.h"

char _database[256] = {0};
char _username[32] = {0};
char _password[32] = {0};
char _timezone[32] = {0};
char _schema[32] = {0};

int _db_init(
    char const * new_database,
    char const * new_username,
    char const * new_password,
    char const * new_timezone,
    char const * new_schema)
{
    if (_database != NULL)
    {
        strncpy(_database, new_database, strnlen(new_database, 127));
    }
    if (_username != NULL)
    {
        strncpy(_username, new_username, strnlen(new_database, 31));
    }
    if (_password != NULL)
    {
        strncpy(_password, new_password, strnlen(new_database, 31));
    }
    if (_timezone != NULL)
    {
        strncpy(_timezone, new_timezone, strnlen(new_database, 31));
    }
    if (_schema != NULL)
    {
        strncpy(_schema, new_schema, strnlen(new_database, 31));
    }
    return OK;
}

int _connect_to_db(struct db_context_t * dbc)
{
    dbc->connection = (nuodb_connection_t *) calloc(1, sizeof(nuodb_connection_t));

    dbc->connection->connection_handle = 0;
    dbc->connection->statement_handle = 0;
    dbc->connection->error = NUODB_ZERO_ERROR;
    dbc->connection->error_message = 0;

    if (NUODB_FAILURE(nuodb_open(dbc->connection)))
    {
        LOG_ERROR_MESSAGE("ERROR: db open failed; %s\n", dbc->connection->error_message);
        return ERROR;
    }
    if (NUODB_FAILURE(nuodb_connect(dbc->connection, _database, _username, _password, _timezone, _schema)))
    {
        LOG_ERROR_MESSAGE("ERROR: db connect failed; %s\n", dbc->connection->error_message);
        return ERROR;
    }

    return OK;
}

int _disconnect_from_db(struct db_context_t *dbc)
{
    if (dbc->connection)
    {
        if (NUODB_FAILURE(nuodb_close(dbc->connection)))
        {
            LOG_ERROR_MESSAGE("ERROR: disconnect failed; %s\n", dbc->connection->error_message);
            return ERROR;
        }
        free(dbc->connection);
        dbc->connection = 0;
    }

    return OK;
}

int commit_transaction(struct db_context_t *dbc)
{
    if (NUODB_FAILURE(nuodb_commit(dbc->connection)))
    {
        LOG_ERROR_MESSAGE("ERROR: commit failed; %s\n", dbc->connection->error_message);
        return ERROR;
    }
    return OK;
}

int rollback_transaction(struct db_context_t * dbc)
{
    if (NUODB_FAILURE(nuodb_rollback(dbc->connection)))
    {
        LOG_ERROR_MESSAGE("ERROR: rollback failed; %s\n", dbc->connection->error_message);
        return ERROR;
    }

    return STATUS_ROLLBACK;
}

int dbt2_sql_execute(struct db_context_t *dbc, char const * query, struct sql_result_t * sql_result,
                     char const * query_name)
{
    sql_result->num_fields = 0;
    sql_result->num_rows = 0;
    sql_result->query = query;

    sql_result->result_set = (nuodb_result_t *) calloc(1, sizeof(nuodb_result_t));

    sql_result->result_set->connection_handle = 0;
    sql_result->result_set->result_handle = 0;
    sql_result->result_set->connection = dbc->connection;

    if (NUODB_FAILURE(nuodb_execute(dbc->connection, query, sql_result->result_set)))
    {
        LOG_ERROR_MESSAGE("ERROR: executing query failed; %s\n", dbc->connection->error_message);
        return ERROR;
    }

    return OK;
}

/**
 * Return non-zero when there are more rows to fetch.
 */
int dbt2_sql_fetchrow(struct db_context_t *dbc, struct sql_result_t * sql_result)
{
    if (NUODB_FAILURE(nuodb_result_next(sql_result->result_set)))
    {
        return ERROR;
    }

    return OK;
}

char * dbt2_sql_getvalue(struct db_context_t *dbc, struct sql_result_t * sql_result, int nth_column)
{
    char const * value = NULL;
    if (NUODB_FAILURE(nuodb_result_fetch_string(sql_result->result_set, nth_column + 1, &value)))
    {
        LOG_ERROR_MESSAGE("ERROR: getting value failed; %s\n", dbc->connection->error_message);
        return ERROR;
    }

    return (char *) value; // known warning; a crappy dbt api
}

int dbt2_sql_close_cursor(struct db_context_t *dbc, struct sql_result_t * sql_result)
{
    if (sql_result->result_set)
    {
        if (NUODB_FAILURE(nuodb_result_free(sql_result->result_set)))
        {
            LOG_ERROR_MESSAGE("ERROR: freeing result failed; %s\n", dbc->connection->error_message);
            return ERROR;
        }
        free(sql_result->result_set);
        sql_result->result_set = 0;
    }

    return OK;
}
