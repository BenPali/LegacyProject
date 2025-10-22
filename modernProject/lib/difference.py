from typing import List, Tuple, TypeVar, Callable

T = TypeVar('T')


class DiagReturn(Exception):
    def __init__(self, diagonal_index: int):
        self.value = diagonal_index
        super().__init__(diagonal_index)


def diag(forward_diagonals: List[int], backward_diagonals: List[int], shift: int,
         get_x_element: Callable[[int], T], get_y_element: Callable[[int], T],
         x_offset: int, x_limit: int, y_offset: int, y_limit: int) -> int:
    diagonal_min = x_offset - y_limit
    diagonal_max = x_limit - y_offset
    forward_mid = x_offset - y_offset
    backward_mid = x_limit - y_limit
    is_odd_delta = ((forward_mid - backward_mid) & 1) != 0

    forward_diagonals[shift + forward_mid] = x_offset
    backward_diagonals[shift + backward_mid] = x_limit

    try:
        forward_min = forward_mid
        forward_max = forward_mid
        backward_min = backward_mid
        backward_max = backward_mid

        while True:
            if forward_min > diagonal_min:
                forward_diagonals[shift + forward_min - 2] = -1
                forward_min -= 1
            else:
                forward_min += 1

            if forward_max < diagonal_max:
                forward_diagonals[shift + forward_max + 2] = -1
                forward_max += 1
            else:
                forward_max -= 1

            diagonal = forward_max
            while diagonal >= forward_min:
                from_lower = forward_diagonals[shift + diagonal - 1]
                from_upper = forward_diagonals[shift + diagonal + 1]
                x_position = from_lower + 1 if from_lower >= from_upper else from_upper
                y_position = x_position - diagonal

                while x_position < x_limit and y_position < y_limit and get_x_element(x_position) is get_y_element(y_position):
                    x_position += 1
                    y_position += 1

                forward_diagonals[shift + diagonal] = x_position

                if is_odd_delta and backward_min <= diagonal <= backward_max:
                    if backward_diagonals[shift + diagonal] <= forward_diagonals[shift + diagonal]:
                        raise DiagReturn(diagonal)

                diagonal -= 2

            if backward_min > diagonal_min:
                backward_diagonals[shift + backward_min - 2] = 2147483647
                backward_min -= 1
            else:
                backward_min += 1

            if backward_max < diagonal_max:
                backward_diagonals[shift + backward_max + 2] = 2147483647
                backward_max += 1
            else:
                backward_max -= 1

            diagonal = backward_max
            while diagonal >= backward_min:
                from_lower = backward_diagonals[shift + diagonal - 1]
                from_upper = backward_diagonals[shift + diagonal + 1]
                x_position = from_lower if from_lower < from_upper else from_upper - 1
                y_position = x_position - diagonal

                while x_position > x_offset and y_position > y_offset:
                    if get_x_element(x_position - 1) is get_y_element(y_position - 1):
                        x_position -= 1
                        y_position -= 1
                    else:
                        break

                backward_diagonals[shift + diagonal] = x_position

                if not is_odd_delta and forward_min <= diagonal <= forward_max:
                    if backward_diagonals[shift + diagonal] <= forward_diagonals[shift + diagonal]:
                        raise DiagReturn(diagonal)

                diagonal -= 2
    except DiagReturn as exception:
        return exception.value


def diff_loop(array_a: List[T], indices_a: List[int], array_b: List[T], indices_b: List[int],
              count_a: int, count_b: int) -> Tuple[List[bool], List[bool]]:
    forward_diagonals = [0] * (count_a + count_b + 3)
    backward_diagonals = [0] * (count_a + count_b + 3)
    shift = count_b + 1

    def get_a_element(index: int) -> T:
        return array_a[indices_a[index]]

    def get_b_element(index: int) -> T:
        return array_b[indices_b[index]]

    changes_in_a = [True] * len(array_a)
    changes_in_b = [True] * len(array_b)

    for index in range(count_a):
        changes_in_a[indices_a[index]] = False

    for index in range(count_b):
        changes_in_b[indices_b[index]] = False

    def find_differences(x_offset: int, x_limit: int, y_offset: int, y_limit: int) -> None:
        current_x_offset = x_offset
        current_y_offset = y_offset

        while current_x_offset < x_limit and current_y_offset < y_limit:
            if get_a_element(current_x_offset) is get_b_element(current_y_offset):
                current_x_offset += 1
                current_y_offset += 1
            else:
                break

        current_x_limit = x_limit
        current_y_limit = y_limit

        while current_x_limit > current_x_offset and current_y_limit > current_y_offset:
            if get_a_element(current_x_limit - 1) is get_b_element(current_y_limit - 1):
                current_x_limit -= 1
                current_y_limit -= 1
            else:
                break

        if current_x_offset == current_x_limit:
            for y_index in range(current_y_offset, current_y_limit):
                changes_in_b[indices_b[y_index]] = True
        elif current_y_offset == current_y_limit:
            for x_index in range(current_x_offset, current_x_limit):
                changes_in_a[indices_a[x_index]] = True
        else:
            diagonal = diag(forward_diagonals, backward_diagonals, shift,
                          get_a_element, get_b_element,
                          current_x_offset, current_x_limit, current_y_offset, current_y_limit)
            split_point = backward_diagonals[shift + diagonal]
            find_differences(current_x_offset, split_point, current_y_offset, split_point - diagonal)
            find_differences(split_point, current_x_limit, split_point - diagonal, current_y_limit)

    find_differences(0, count_a, 0, count_b)
    return (changes_in_a, changes_in_b)


def make_indexer(source_array: List[T], reference_array: List[T]) -> List[int]:
    source_length = len(source_array)
    unique_elements = {}

    for index in range(len(reference_array)):
        element = reference_array[index]
        if element not in unique_elements:
            unique_elements[element] = element
        reference_array[index] = unique_elements[element]

    matching_indices = [0] * source_length
    match_count = 0

    for index in range(source_length):
        element = source_array[index]
        if element in unique_elements:
            source_array[index] = unique_elements[element]
            matching_indices[match_count] = index
            match_count += 1

    return matching_indices[:match_count]


def f(array_a: List[T], array_b: List[T]) -> Tuple[List[bool], List[bool]]:
    indices_a = make_indexer(array_a, array_b)
    indices_b = make_indexer(array_b, array_a)
    count_a = len(indices_a)
    count_b = len(indices_b)
    return diff_loop(array_a, indices_a, array_b, indices_b, count_a, count_b)
