PROJECT(dbt2 C CXX)
CMAKE_MINIMUM_REQUIRED(VERSION 2.6.0)

INCLUDE(CheckFunctionExists)
INCLUDE(CheckLibraryExists)

SET(CPACK_CMAKE_GENERATOR "Unix Makefiles")
SET(CPACK_PACKAGE_NAME "DBT2")
SET(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Database Test 2")
SET(CPACK_PACKAGE_VERSION_MAJOR "0")
SET(CPACK_PACKAGE_VERSION_MINOR "42")
SET(CPACK_PACKAGE_VERSION_PATCH "0")
SET(CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}")
SET(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}")
SET(CPACK_GENERATOR "TGZ")
SET(CPACK_PACKAGE_VENDOR "NuoDB")
SET(CPACK_PACKAGE_DESCRIPTION_FILE "README-INTRO")
SET(CPACK_RESOURCE_FILE_LICENSE "LICENSE")
INCLUDE(CPack)

CHECK_FUNCTION_EXISTS(bind HAVE_BIND)
CHECK_FUNCTION_EXISTS(recv HAVE_RECV)
CHECK_FUNCTION_EXISTS(send HAVE_SEND)
CHECK_FUNCTION_EXISTS(accept HAVE_ACCEPT)
CHECK_FUNCTION_EXISTS(listen HAVE_LISTEN)
CHECK_FUNCTION_EXISTS(getprotobyname HAVE_GETPROTOBYNAME)
CHECK_FUNCTION_EXISTS(socket HAVE_SOCKET)
CHECK_FUNCTION_EXISTS(setsockopt HAVE_SETSOCKOPT)
CHECK_FUNCTION_EXISTS(connect HAVE_CONNECT)
CHECK_FUNCTION_EXISTS(nanosleep HAVE_NANOSLEEP)

ADD_DEFINITIONS(-D_REENTRANT)
ADD_DEFINITIONS(-D_PTHREAD_SAFE)

IF (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    ADD_DEFINITIONS(-D_GNU_SOURCE)
    ADD_DEFINITIONS(-D_POSIX_C_SOURCE=199309L)
    CHECK_LIBRARY_EXISTS("rt" "sem_init" "" HAVE_LIBRT)
ELSEIF (${CMAKE_SYSTEM_NAME} MATCHES "Solaris")
    ADD_DEFINITIONS(-D_POSIX_C_SOURCE=199309L)
    ADD_DEFINITIONS(-D_PTHREADS)
    CHECK_LIBRARY_EXISTS(socket bind "" HAVE_LIBSOCKET)
    CHECK_LIBRARY_EXISTS(nsl gethostbyaddr "" HAVE_LIBNSL)
ENDIF (${CMAKE_SYSTEM_NAME} MATCHES "Linux")

IF (CMAKE_SIZEOF_VOID_P MATCHES "8")
    EXECUTE_PROCESS(
        COMMAND
            getconf LFS64_CFLAGS
        OUTPUT_VARIABLE
            LFS_CFLAGS
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE
        )
ELSE (CMAKE_SIZEOF_VOID_P MATCHES "8")
    EXECUTE_PROCESS(
        COMMAND
            getconf LFS_CFLAGS
        OUTPUT_VARIABLE
            LFS_CFLAGS
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE
        )
ENDIF (CMAKE_SIZEOF_VOID_P MATCHES "8")

#
# Defining binaries so to minimized typoes.
#

SET(DBT2_CLIENT bin/dbt2-client)
SET(DBT2_DATAGEN bin/dbt2-datagen)
SET(DBT2_DRIVER bin/dbt2-driver)
SET(DBT2_TXN_TEST bin/dbt2-transaction-test)

IF (DBMS STREQUAL "pgsql")
    #
    # Create PostgreSQL specific configuration.
    #

    FIND_PROGRAM(PG_CONFIG pg_config)

    IF (PG_CONFIG)
       SET(PG_CONFIG_FOUND TRUE)
    ENDIF (PG_CONFIG)

    IF (PG_CONFIG_FOUND)
        MESSAGE(STATUS "Found pg_config for PostgreSQL: ${PG_CONFIG}")
        SET(DB_SOURCE src/libpq/dbc_common.c src/libpq/dbc_new_order.c
                src/libpq/dbc_payment.c src/libpq/dbc_order_status.c
                src/libpq/dbc_delivery.c src/libpq/dbc_stock_level.c
                src/libpq/dbc_integrity.c)
        EXECUTE_PROCESS(COMMAND ${PG_CONFIG} --includedir OUTPUT_VARIABLE
                PG_INCLUDEDIR OUTPUT_STRIP_TRAILING_WHITESPACE)
        EXECUTE_PROCESS(COMMAND ${PG_CONFIG} --libdir OUTPUT_VARIABLE
                PG_LIBDIR OUTPUT_STRIP_TRAILING_WHITESPACE)
        SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DLIBPQ -I${PG_INCLUDEDIR}")
        SET(DB_LIBS "-L${PG_LIBDIR} -lpq")
        SET(DB_SCRIPTS bin/pgsql/dbt2-pgsql-build-db
                bin/pgsql/dbt2-pgsql-check-db
                bin/pgsql/dbt2-pgsql-create-db
                bin/pgsql/dbt2-pgsql-create-indexes
                bin/pgsql/dbt2-pgsql-create-tables bin/pgsql/dbt2-pgsql-db-stat
                bin/pgsql/dbt2-pgsql-drop-db bin/pgsql/dbt2-pgsql-drop-tables
                bin/pgsql/dbt2-pgsql-load-db
                bin/pgsql/dbt2-pgsql-load-stored-procs
                bin/pgsql/dbt2-pgsql-plans bin/pgsql/dbt2-pgsql-start-db
                bin/pgsql/dbt2-pgsql-stop-db)
    ELSE (NOT DEFINED PKG_CONFIG_FOUND)
        MESSAGE(FATAL_ERROR "pg_config not found in path")
    ENDIF (PG_CONFIG_FOUND)
ELSEIF (DBMS STREQUAL "sqlite")
    FIND_PROGRAM(PKG_CONFIG pkg-config)

    IF (PKG_CONFIG)
       SET(PKG_CONFIG_FOUND TRUE)
    ENDIF (PKG_CONFIG)

    IF (PKG_CONFIG_FOUND)
        SET(DB_SOURCE src/sqlite/dbc_common.c src/nonsp/dbc_new_order.c
                src/nonsp/dbc_payment.c src/nonsp/dbc_order_status.c
                src/nonsp/dbc_delivery.c src/nonsp/dbc_stock_level.c
                src/nonsp/dbc_integrity.c src/nonsp/dbc_nonsp.c)
        EXECUTE_PROCESS(COMMAND ${PKG_CONFIG} --cflags sqlite3 OUTPUT_VARIABLE
                SQLITE_CFLAGS OUTPUT_STRIP_TRAILING_WHITESPACE)
        EXECUTE_PROCESS(COMMAND ${PKG_CONFIG} --libs sqlite3 OUTPUT_VARIABLE
                DB_LIBS OUTPUT_STRIP_TRAILING_WHITESPACE)
        SET(DBCFLAGS "-DLIBSQLITE ${SQLITE_CFLAGS}")
        SET(DB_SCRIPTS bin/sqlite/dbt2-sqlite-build-db
                bin/sqlite/dbt2-sqlite-plans bin/sqlite/dbt2-sqlite-start-db
                bin/sqlite/dbt2-sqlite-stop-db)
    ENDIF (PKG_CONFIG_FOUND)
ELSEIF (DBMS STREQUAL "mysql")
    #
    # Create MySQL specific configuration.
    #

    FIND_PROGRAM(MYSQL_CONFIG mysql_config)

    IF (MYSQL_CONFIG)
        SET(MYSQL_CONFIG_FOUND TRUE)
    ENDIF (MYSQL_CONFIG)

    IF(NOT DEFINED MYSQL)
        SET(MYSQL /usr/bin/sql )
    ENDIF(NOT DEFINED MYSQL)

    IF (MYSQL_CONFIG_FOUND)
        MESSAGE(STATUS "Found mysql_config for MySQL: ${MYSQL_CONFIG}")

		IF (NONSP MATCHES "1")
		  SET(DB_SOURCE src/mysql/dbc_common.c
                       src/nonsp/dbc_new_order.c
                       src/nonsp/dbc_payment.c
                       src/nonsp/dbc_order_status.c
                       src/nonsp/dbc_delivery.c
                       src/nonsp/dbc_stock_level.c
                       src/nonsp/dbc_nonsp.c
                       src/nonsp/dbc_integrity.c)
		ELSE(NONSP MATCHES "1")
          SET(DB_SOURCE src/mysql/dbc_common.c
		  			   src/mysql/dbc_new_order.c
					   src/mysql/dbc_payment.c
					   src/mysql/dbc_order_status.c
					   src/mysql/dbc_delivery.c
					   src/mysql/dbc_stock_level.c
					   src/mysql/dbc_integrity.c)
		ENDIF(NONSP MATCHES "1")

        EXECUTE_PROCESS(COMMAND ${MYSQL_CONFIG} --include OUTPUT_VARIABLE
                MYSQL_INCLUDE_CFLAGS OUTPUT_STRIP_TRAILING_WHITESPACE)
        EXECUTE_PROCESS(COMMAND ${MYSQL_CONFIG} --libs OUTPUT_VARIABLE
                DB_LIBS OUTPUT_STRIP_TRAILING_WHITESPACE)
        SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DLIBMYSQL ${MYSQL_INCLUDE_CFLAGS}")
        SET(DB_SCRIPTS
                bin/mysql/dbt2-mysql-build-db
                bin/mysql/dbt2-mysql-load-stored-procs
                bin/mysql/dbt2-mysql-plans
                bin/mysql/dbt2-mysql-start-db
                bin/mysql/dbt2-mysql-stop-db)
    ENDIF (MYSQL_CONFIG_FOUND)
ELSEIF (DBMS STREQUAL "drizzle")
    #
    # Create Drizzle specific configuration.
    #

    SET(DB_SOURCE src/drizzle/dbc_common.c
                       src/nonsp/dbc_new_order.c
                       src/nonsp/dbc_payment.c
                       src/nonsp/dbc_order_status.c
                       src/nonsp/dbc_delivery.c
                       src/nonsp/dbc_stock_level.c
                       src/nonsp/dbc_nonsp.c
                       src/nonsp/dbc_integrity.c)

    IF(NOT DEFINED DRIZZLE_INCLUDEDIR)
        SET(DRIZZLE_INCLUDEDIR /usr/local/include )
    ENDIF(NOT DEFINED DRIZZLE_INCLUDEDIR)

    IF(NOT DEFINED DRIZZLE_LIBS)
        SET(DB_LIBS "-ldrizzle  -lpthread")
    ENDIF(NOT DEFINED DRIZZLE_LIBS)

    SET(DBCFLAGS "-DLIBDRIZZLE -I${DRIZZLE_INCLUDEDIR}")

    MESSAGE(STATUS "Drizzle configuration build flags :  ${DBCFLAGS}")
    MESSAGE(STATUS "Drizzle configuration library flags:  ${DB_LIBS}")

    SET(DB_SCRIPTS bin/drizzle/dbt2-drizzle-admin
            bin/drizzle/dbt2-drizzle-load-db
            bin/drizzle/dbt2-drizzle-start-db
            bin/drizzle/dbt2-drizzle-stop-db)

ELSEIF (DBMS STREQUAL "nuodb")
    
    # #########################################################################
    # NUODB SECTION
    # #########################################################################

    SET(DB_SCRIPTS bin/nuodb/dbt2-nuodb-load-db
            bin/nuodb/dbt2-nuodb-start-db
            bin/nuodb/dbt2-nuodb-stop-db
            bin/nuodb/dbt2-nuodb-profile)

    FIND_PATH(NUODB_INCLUDE_DIR Connection.h
        PATHS $ENV{NUODB_INCLUDE_DIR}
        DOC "NuoDB includes directory")

    IF(NUODB_INCLUDE_DIR)
        MESSAGE(STATUS "NuoRemote includes directory found: " ${NUODB_INCLUDE_DIR})
    ELSE(NUODB_INCLUDE_DIR)
        MESSAGE(WARNING "NuoRemote includes directory not found; please set NUODB_INCLUDE_DIR variable")
    ENDIF(NUODB_INCLUDE_DIR)

    FIND_LIBRARY(NUOREMOTE_LIBRARY
        NAMES NuoRemote libNuoRemote
        PATHS $ENV{NUODB_LIB_DIR}
        DOC "NuoDB library to link against")

    IF(NUOREMOTE_LIBRARY)
        MESSAGE(STATUS "NuoRemote library found: " ${NUOREMOTE_LIBRARY})
    ELSE(NUOREMOTE_LIBRARY)
        MESSAGE(WARNING "NuoRemote library not found; please set NUODB_LIB_DIR variable")
    ENDIF(NUOREMOTE_LIBRARY)
    
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DNUODB -I${NUODB_INCLUDE_DIR}")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DNUODB -I${NUODB_INCLUDE_DIR}")

    SET(DB_LIBS "-L$ENV{NUODB_LIB_DIR} -lNuoRemote")
    
    IF(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
        SET(CMAKE_EXE_LINKER_FLAGS "-Xlinker -rpath -Xlinker $ENV{NUODB_LIB_DIR}")
    ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")

    IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
        SET(CMAKE_EXE_LINKER_FLAGS "-Wl,-rpath,'$$ORIGIN'")
    ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")

    IF (NONSP MATCHES "1")
        SET(DB_SOURCE src/nuodb/dbc_common.c
            src/nuodb/nuodb_capi.cpp
            src/nuodb/dbc_new_order_nonsp.c
            src/nuodb/dbc_stock_level_nonsp.c
            src/nonsp/dbc_payment.c
            src/nonsp/dbc_order_status.c
            src/nonsp/dbc_delivery.c
            src/nonsp/dbc_nonsp.c
            src/nonsp/dbc_integrity.c)
    ELSE(NONSP MATCHES "1")
        SET(DB_SOURCE src/nuodb/dbc_common.c
            src/nuodb/nuodb_capi.cpp
            src/nuodb/dbc_new_order.c
            src/nuodb/dbc_stock_level.c
            src/nuodb/dbc_payment.c
            src/nuodb/dbc_order_status.c
            src/nuodb/dbc_delivery.c
            src/nonsp/dbc_nonsp.c
            src/nonsp/dbc_integrity.c)
    ENDIF(NONSP MATCHES "1")

ELSE (NOT DEFINED DBMS)
    MESSAGE(FATAL_ERROR "Need to specify -DDBMS=drizzle|mysql|nuodb|pgsql|sqlite")

ENDIF (DBMS STREQUAL "pgsql")

#
# Defining commong groups of source files.
#

SET(COMMON_SOURCE src/common.c src/logging.c src/_socket.c
        src/client_interface.c src/transaction_data.c src/_semaphore.c)

#
# Files to build.
#

ADD_EXECUTABLE(${DBT2_CLIENT} src/client.c src/transaction_queue.c
        src/listener.c src/db_threadpool.c src/db.c ${COMMON_SOURCE}
        ${DB_SOURCE})

IF (HAVE_LIBRT)
    TARGET_LINK_LIBRARIES(${DBT2_CLIENT} rt)
ENDIF (HAVE_LIBRT)
IF (HAVE_LIBSOCKET)
    TARGET_LINK_LIBRARIES(${DBT2_CLIENT} socket)
ENDIF (HAVE_LIBSOCKET)
IF (HAVE_LIBNSL)
    TARGET_LINK_LIBRARIES(${DBT2_CLIENT} nsl)
ENDIF (HAVE_LIBNSL)

ADD_EXECUTABLE(${DBT2_DATAGEN} src/datagen.c src/common.c)

ADD_EXECUTABLE(${DBT2_DRIVER} ${COMMON_SOURCE} src/driver_main.c src/driver.c
        src/input_data_generator.c)

IF (HAVE_LIBRT)
    TARGET_LINK_LIBRARIES(${DBT2_DRIVER} rt)
ENDIF (HAVE_LIBRT)
IF (HAVE_LIBSOCKET)
    TARGET_LINK_LIBRARIES(${DBT2_DRIVER} socket)
ENDIF (HAVE_LIBSOCKET)
IF (HAVE_LIBNSL)
    TARGET_LINK_LIBRARIES(${DBT2_DRIVER} nsl)
ENDIF (HAVE_LIBNSL)

ADD_EXECUTABLE(${DBT2_TXN_TEST} src/transaction_test.c src/db.c
        src/input_data_generator.c ${COMMON_SOURCE} ${DB_SOURCE})

IF (HAVE_LIBSOCKET)
    TARGET_LINK_LIBRARIES(${DBT2_TXN_TEST} socket)
ENDIF (HAVE_LIBSOCKET)
IF (HAVE_LIBNSL)
    TARGET_LINK_LIBRARIES(${DBT2_TXN_TEST} nsl)
ENDIF (HAVE_LIBNSL)

#
# Set compiler flags.
#

SET(WARNINGS_CFLAGS "-Wall -Wextra -pedantic -Wno-unused-parameter -Wshadow -Wpointer-arith -fno-strict-aliasing -fno-builtin -Wcast-qual -Wcast-align -fstrict-aliasing -Wno-long-long  -Wwrite-strings -fPIC -m64")
SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${WARNINGS_CFLAGS} -std=c99 -Isrc/include ${LFS_CFLAGS}")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${WARNINGS_CFLAGS} -Isrc/include ${LFS_CFLAGS}")

SET(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -DDEBUG=1 -ggdb")
SET(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -DNDEBUG=1")
SET(CMAKE_C_FLAGS_RELWITHDEBINFO "${CMAKE_C_FLAGS_RELWITHDEBINFO} -DNDEBUG=1 -ggdb")

SET(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -DDEBUG=1 -ggdb")
SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -DNDEBUG=1")
SET(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} -DNDEBUG=1 -ggdb")

#
# Set linker flags.
#

TARGET_LINK_LIBRARIES(${DBT2_CLIENT} "-lm ${DB_LIBS} -lpthread")
TARGET_LINK_LIBRARIES(${DBT2_DATAGEN} "-lm")
TARGET_LINK_LIBRARIES(${DBT2_DRIVER} "-lm -lpthread")
TARGET_LINK_LIBRARIES(${DBT2_TXN_TEST} "-lm ${DB_LIBS} -lpthread")

#
# Install rules.
#

INSTALL(PROGRAMS ${DBT2_CLIENT} ${DBT2_DATAGEN} ${DBT2_DRIVER} ${DBT2_TXN_TEST}
        bin/dbt2-generate-report bin/dbt2-get-os-info bin/dbt2-post-process
        bin/dbt2-run-workload bin/dbt2-sysstats bin/dbt2-plot-transaction-rate
		bin/dbt2-run-location
        ${DB_SCRIPTS} DESTINATION bin)

# FILE(GLOB DB_STOREDPROCS "${CMAKE_CURRENT_SOURCE_DIR}/storedproc/*.sql")
FILE(GLOB DB_STOREDPROCS "storedproc/${DBMS}/*.sql")
INSTALL(FILES ${DB_STOREDPROCS} DESTINATION storedproc)

