from restaurant import Restaurant
import timeit


def main():
    start = timeit.default_timer()

    ### Editable software part ###
    rest = Restaurant()
    rest.solve()
    ##############################

    stop = timeit.default_timer()
    print('Time: ', stop - start)


if __name__ == '__main__':
    main()