def sort_auto(array=[],reverse=False):
    if len(array) <= 1000:
        return sort_bubble(array,reverse)
    else:
        return sort_merge(array,reverse)

def sort_bubble(array=[],reverse=False):
    mlen=len(array)
    cout_i=0
    while cout_i<mlen:
        cout_j=0
        while cout_j<mlen-1:
            if array[cout_j-1] > array[cout_j]:
                tmp=array[cout_j-1]
                array[cout_j-1]=array[cout_j]
                array[cout_j]=tmp
            cout_j=cout_j+1
        cout_i=cout_i+1
    if reverse:
        array.reverse()
    return array

def sort_merge(x,reverse=False):
    result = []
    if len(x) < 2:
        return x
    mid = int(len(x)/2)
    y = sort_merge(x[:mid])
    z = sort_merge(x[mid:])
    while (len(y) > 0) or (len(z) > 0):
        if len(y) > 0 and len(z) > 0:
            if y[0] > z[0]:
                result.append(z[0])
                z.pop(0)
            else:
                result.append(y[0])
                y.pop(0)
        elif len(z) > 0:
            for i in z:
                result.append(i)
                z.pop(0)
        else:
            for i in y:
                result.append(i)
                y.pop(0)
    if reverse:
        result.reverse()
    return result
