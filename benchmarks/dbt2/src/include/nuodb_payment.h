#ifndef _NUODB_PAYMENT_H_
#define _NUODB_PAYMENT_H_

#include "nuodb_common.h"

int execute_payment(struct db_context_t *dbc, struct payment_t *data);

#endif /* _NUODB_PAYMENT_H_ */