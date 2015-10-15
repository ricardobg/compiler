void combsort(int arr[], int size) {
    float shrink_factor = 1.247330950103979;
    int gap = size, swapped = 1, swap, i;
    while ((gap > 1) || swapped) {
        if (gap > 1)
           gap = gap / shrink_factor;

        swapped = 0;
        i = 0;

        while ((gap + i) < size) {
            if (arr[i] - arr[i + gap] > 0) {
                swap = arr[i];
                arr[i] = arr[i + gap];
                arr[i + gap] = swap;
                swapped = 1;
            }
            ++i;
        }
    }
}
