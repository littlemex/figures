// heap_uid.cu: 起動器なしで N 個のプロセスを立て、UID で NVSHMEM を初期化し、対称ヒープのアドレスを並べる
// 使い方: RANK=<i> NRANKS=<n> ./heap_uid（RANK=0 が /dev/shm/nvshmem_uid に UID を書き、他はそれを読む）
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "nvshmem.h"
#include "nvshmemx.h"

__global__ void put_next(int *a, int mype, int npes) {
    nvshmem_int_p(a, mype, (mype + 1) % npes);   // 自分の番号を、次の PE の a[0] に書く
    nvshmem_quiet();                             // GPU から出した put の完了を待つ
}

int main(void) {
    int rank = atoi(getenv("RANK")), nranks = atoi(getenv("NRANKS"));
    int ndev = 0;
    cudaGetDeviceCount(&ndev);
    cudaSetDevice(rank % ndev);
    cudaFree(0);

    nvshmemx_uniqueid_t uid = NVSHMEMX_UNIQUEID_INITIALIZER;
    const char *path = "/dev/shm/nvshmem_uid";
    if (rank == 0) {
        nvshmemx_get_uniqueid(&uid);
        FILE *f = fopen("/dev/shm/nvshmem_uid.tmp", "wb");
        fwrite(&uid, sizeof(uid), 1, f);
        fclose(f);
        rename("/dev/shm/nvshmem_uid.tmp", path);
    } else {
        FILE *f = NULL;
        while (!(f = fopen(path, "rb"))) usleep(10000);
        fread(&uid, sizeof(uid), 1, f);
        fclose(f);
    }
    nvshmemx_init_attr_t attr = NVSHMEMX_INIT_ATTR_INITIALIZER;
    nvshmemx_set_attr_uniqueid_args(rank, nranks, &uid, &attr);
    nvshmemx_init_attr(NVSHMEMX_INIT_WITH_UNIQUEID, &attr);

    int mype = nvshmem_my_pe(), npes = nvshmem_n_pes();
    int *a = (int *)nvshmem_malloc(1 << 20);
    int *b = (int *)nvshmem_malloc(1 << 20);
    nvshmem_barrier_all();
    for (int r = 0; r < npes; r++) {
        if (r == mype) {
            int dev; cudaGetDevice(&dev);
            printf("PE %d (GPU %d): a = %p  b - a = %ld bytes\n", mype, dev, (void *)a,
                   (long)((char *)b - (char *)a));
            for (int pe = 0; pe < npes; pe++)
                printf("PE %d:   nvshmem_ptr(a, PE %d) = %p\n", mype, pe, nvshmem_ptr(a, pe));
            fflush(stdout);
        }
        nvshmem_barrier_all();
    }
    put_next<<<1, 1>>>(a, mype, npes);
    cudaDeviceSynchronize();
    nvshmem_barrier_all();
    int got = -1;
    cudaMemcpy(&got, a, sizeof(int), cudaMemcpyDeviceToHost);
    printf("PE %d received %d via put\n", mype, got);
    fflush(stdout);
    if (getenv("HOLD_SEC")) sleep(atoi(getenv("HOLD_SEC")));
    nvshmem_free(b);
    nvshmem_free(a);
    nvshmem_finalize();
    if (rank == 0) unlink(path);
    return 0;
}
