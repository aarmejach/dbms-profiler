#ifndef _NUODB_CAPI_H_
#define _NUODB_CAPI_H_

#include <stdlib.h>
#include <stdint.h>

#ifdef __cplusplus
#   define NUODB_CFUNC extern "C"
#   define NUODB_CDECL_BEGIN extern "C" {
#   define NUODB_CDECL_END   }
#else
#   define NUODB_CFUNC extern
#   define NUODB_CDECL_BEGIN
#   define NUODB_CDECL_END
#endif

NUODB_CDECL_BEGIN

typedef enum _nuodb_error_code {
    NUODB_WARNING_START = -128,
    NUODB_WARNING_LIMIT,

    NUODB_ZERO_ERROR = 0,

    NUODB_ILLEGAL_ARGUMENT = 1,
    NUODB_INTERNAL_ERROR = 2,
    NUODB_CONNECTION_ERROR = 3,
	NUODB_NO_DATA = 4,
    NUODB_STANDARD_ERROR_LIMIT

} nuodb_error_code;

typedef struct _nuodb_connection_t
{
    uintptr_t connection_handle;
    uintptr_t statement_handle;
    nuodb_error_code error;
    char const * error_message;
} nuodb_connection_t;

typedef struct _nuodb_result_t
{
    uintptr_t connection_handle;
	uintptr_t result_handle;
    nuodb_connection_t * connection;
} nuodb_result_t;

NUODB_CDECL_END

#ifdef __cplusplus
static
inline bool NUODB_SUCCESS(nuodb_error_code code) {
    return (bool)(code <= NUODB_ZERO_ERROR);
}
static
inline bool NUODB_FAILURE(nuodb_error_code code) {
    return (bool)(code > NUODB_ZERO_ERROR);
}
#else
#  define NUODB_SUCCESS(x) ((x) <= NUODB_ZERO_ERROR)
#  define NUODB_FAILURE(x) ((x) > NUODB_ZERO_ERROR)
#endif

NUODB_CFUNC int nuodb_open(
    nuodb_connection_t * connection);

NUODB_CFUNC int nuodb_connect(
    nuodb_connection_t * connection,
    char const * database,
    char const * username,
    char const * password,
    char const * timezone,
    char const * schema);

NUODB_CFUNC int nuodb_close(
    nuodb_connection_t * connection);

NUODB_CFUNC int nuodb_commit(
	nuodb_connection_t * connection);

NUODB_CFUNC int nuodb_rollback(
	nuodb_connection_t * connection);

NUODB_CFUNC int nuodb_execute(
	nuodb_connection_t * connection,
	char const * query,
	nuodb_result_t * result);

NUODB_CFUNC int nuodb_result_free(
	nuodb_result_t * result);

NUODB_CFUNC int nuodb_result_next(
	nuodb_result_t * result);

NUODB_CFUNC int nuodb_result_fetch_fields(
	nuodb_result_t * result,
	size_t * column_count);

NUODB_CFUNC int nuodb_result_fetch_string(
	nuodb_result_t * result,
	size_t column,
	char const ** value);

#endif /* _NUODB_CAPI_H_ */
