/* For the size of the file. */
#include <sys/stat.h>
#include <sys/mman.h> 
#include <errno.h>
#include <string.h>
#include <stdarg.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

static void
check (int test, const char * message, ...)
{
    if (test) {
            va_list args;
            va_start (args, message);
            vfprintf (stderr, message, args);
            va_end (args);
            fprintf (stderr, "\n");
            exit (EXIT_FAILURE);
        }
}

int main (int argc, char *argv[])
{
    /* The file descriptor. */
    int fd;
    /* Information about the file. */
    struct stat s;
    int status;
    size_t size;
    /* The file name to open. */
    const char * file_name = "16410";
    /* The memory-mapped thing itself. */
    const char * mapped;
    int i;

    /* Open the file for reading. */
    fd = open (file_name, O_RDONLY);
    check (fd < 0, "open %s failed: %s", file_name, strerror (errno));

    /* Get the size of the file. */
    status = fstat (fd, & s);
    check (status < 0, "stat %s failed: %s", file_name, strerror (errno));
    size = s.st_size;

    printf("File %s opened in fd %d, size %lu", file_name, fd, size);
    /* Memory-map the file. */
    mapped = mmap (NULL, size, PROT_READ, MAP_SHARED, fd, 0);
    check (mapped == MAP_FAILED, "mmap %s failed: %s",
                       file_name, strerror (errno));

    /* Now do something with the information. */
    for (i = 0; i < size; i++) {
            char c;

            c = mapped[i];
            if (! isalpha (c) && ! isspace (c)) {
                        putchar (c);
            }
            if (i % 80 == 79) {
                        putchar ('\n');
            }
    }

    return 0;
}
