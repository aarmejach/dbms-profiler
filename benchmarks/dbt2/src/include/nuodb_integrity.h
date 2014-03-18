#ifndef _NUODB_INTEGRITY_H_
#define _NUODB_INTEGRITY_H_

#include <nuodb_common.h>
#include <transaction_data.h>

int execute_integrity(struct db_context_t *dbc, struct integrity_t *data);

#endif /* _NUODB_INTEGRITY_H_ */
