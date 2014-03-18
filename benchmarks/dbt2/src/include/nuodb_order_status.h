#ifndef _NUODB_ORDER_STATUS_H_
#define _NUODB_ORDER_STATUS_H_

#include "nuodb_common.h"

int execute_order_status(struct db_context_t *dbc, struct order_status_t *data);

#endif /* _NUODB_ORDER_STATUS_H_ */