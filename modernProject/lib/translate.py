from typing import Optional, Tuple, Callable, List, Set
from modernProject.lib import buff

def find_language_code_end(text: str, start: int = 0) -> Optional[int]:
    position = start
    while position < len(text):
        char = text[position]
        if char.isalpha() or char == '-':
            position += 1
        else:
            return position
    return None

def inline(target_lang: str, macro_char: str, macro_expander: Callable[[str], str], text: str) -> Tuple[str, bool]:
    target_lang_prefix = target_lang + ":"

    base_lang_prefix = ""
    if '-' in target_lang:
        base_lang_prefix = target_lang.split('-')[0] + ":"

    def scan_for_language(fallback_text: Optional[str], at_line_start: bool, position: int) -> Tuple[str, bool]:
        if position >= len(text):
            if fallback_text is not None:
                return (fallback_text, True)
            return ("..........", False)

        if not at_line_start:
            next_line_start = text[position] == '\n'
            return scan_for_language(fallback_text, next_line_start, position + 1)

        lang_end = find_language_code_end(text, position)
        if lang_end is None or lang_end >= len(text) or text[lang_end] != ':':
            next_line_start = text[position] == '\n'
            return scan_for_language(fallback_text, next_line_start, position + 1)

        current_lang = text[position:lang_end + 1]
        is_match = (current_lang == target_lang_prefix or
                   current_lang == base_lang_prefix or
                   current_lang == "en:")

        if not is_match:
            next_line_start = text[position] == '\n'
            return scan_for_language(fallback_text, next_line_start, position + 1)

        content_start = lang_end + 2 if (lang_end + 1 < len(text) and text[lang_end + 1] == ' ') else lang_end + 1

        def extract_line_content(buffer_length: int, pos: int) -> Tuple[str, int]:
            if pos >= len(text):
                return (buff.get(buffer_length), pos)

            if text[pos] == '\n':
                if pos + 1 < len(text) and text[pos + 1] == ' ':
                    skip_pos = pos + 1
                    while skip_pos < len(text) and text[skip_pos] == ' ':
                        skip_pos += 1
                    new_length = buff.store(buffer_length, '\n')
                    return extract_line_content(new_length, skip_pos)
                return (buff.get(buffer_length), pos)

            if text[pos] == macro_char and pos + 1 < len(text):
                expansion = macro_expander(text[pos + 1])
                new_length = buff.mstore(buffer_length, expansion)
                return extract_line_content(new_length, pos + 2)

            new_length = buff.store(buffer_length, text[pos])
            return extract_line_content(new_length, pos + 1)

        extracted_text, next_position = extract_line_content(0, content_start)

        if current_lang == target_lang_prefix:
            return (extracted_text, False)

        updated_fallback = fallback_text
        if current_lang == base_lang_prefix or fallback_text is None:
            updated_fallback = extracted_text

        return scan_for_language(updated_fallback, True, next_position)

    return scan_for_language(None, True, 0)

def language_name(lang: str, lang_def: str, sep: str = '/') -> str:
    lang_len = len(lang)
    i = 0
    beg = 0

    while i <= len(lang_def):
        if i == len(lang_def) and i == beg:
            return lang
        elif i == len(lang_def) or lang_def[i] == sep:
            if (i > beg + lang_len + 1 and
                lang_def[beg + lang_len] == '=' and
                lang_def[beg:beg + lang_len] == lang):
                return lang_def[beg + lang_len + 1:i]
            elif i == len(lang_def):
                return lang
            else:
                beg = i + 1
                i = beg
        else:
            i += 1

    return lang

def remove_substring(text: str, start: int, end: int) -> str:
    return text[:start] + text[end:]

def extract_grammar_flags(text: str) -> Tuple[Set[str], str]:
    flags = set()
    result = text
    position = 0

    while position + 3 < len(result):
        if result[position] != '@' or result[position + 1] != '(':
            position += 1
            continue

        if result[position + 3] == '?' or result[position + 3] == '-':
            position += 1
            continue

        if result[position + 2] == '&' and result[position + 3] == ')':
            if position + 4 < len(result):
                result = remove_substring(result, position, position + 5)
            continue

        closing_paren = position + 2
        while closing_paren < len(result) and result[closing_paren] != ')':
            flags.add(result[closing_paren])
            closing_paren += 1

        if closing_paren < len(result):
            closing_paren += 1

        result = remove_substring(result, position, closing_paren)

    return (flags, result)

def evaluate_conditional_expression(active_flags: Set[str], text: str, position: int) -> Tuple[str, int]:
    if position >= len(text):
        return (text, position)

    if position + 1 >= len(text) or text[position + 1] != '?':
        if text[position] in (':', ')'):
            return (text, position)
        return evaluate_conditional_expression(active_flags, text, position + 1)

    flag_to_check = text[position]
    condition_is_true = flag_to_check in active_flags

    if condition_is_true:
        text_without_condition = remove_substring(text, position, position + 2)
        text_with_true_branch, end_position = evaluate_conditional_expression(active_flags, text_without_condition, position)

        if end_position < len(text_with_true_branch) and text_with_true_branch[end_position] == ':':
            text_with_false_removed, false_end = evaluate_conditional_expression(active_flags, text_with_true_branch, end_position + 1)
            return (remove_substring(text_with_false_removed, end_position, false_end), end_position)

        return (text_with_true_branch, end_position)

    text_after_condition, true_branch_end = evaluate_conditional_expression(active_flags, text, position + 2)
    text_without_true_branch = remove_substring(text_after_condition, position, true_branch_end)

    if position < len(text_without_true_branch) and text_without_true_branch[position] == ':':
        text_without_colon = remove_substring(text_without_true_branch, position, position + 1)
        return evaluate_conditional_expression(active_flags, text_without_colon, position)

    return (text_without_true_branch, position)

def apply_conditional_expressions(active_flags: Set[str], text: str) -> str:
    result = text
    position = 0

    while position + 3 < len(result):
        if result[position] == '@' and result[position + 1] == '(' and result[position + 3] != '-':
            result = remove_substring(result, position, position + 2)
            result, end_position = evaluate_conditional_expression(active_flags, result, position)

            if end_position < len(result) and result[end_position] == ')':
                result = remove_substring(result, end_position, end_position + 1)
            else:
                position = end_position
        else:
            position += 1

    return result

def shift_words_in_text(text: str) -> str:
    output_buffer = ['#'] * len(text)
    read_pos = 0
    write_pos = 0
    made_changes = False

    while read_pos < len(text):
        is_shift_command = (read_pos + 4 < len(text) and
                           text[read_pos] == '@' and
                           text[read_pos + 1] == '(' and
                           text[read_pos + 2].isdigit() and
                           text[read_pos + 3] == '-')

        if not is_shift_command:
            output_buffer[write_pos] = text[read_pos]
            read_pos += 1
            write_pos += 1
            continue

        words_to_move = int(text[read_pos + 2])
        move_to_end = (read_pos + 4 < len(text) and text[read_pos + 4] == '-')
        command_end = (read_pos + 5) if move_to_end else (read_pos + 4)

        if command_end >= len(text) or text[command_end] != ')':
            output_buffer[write_pos] = text[read_pos]
            read_pos += 1
            write_pos += 1
            continue

        segment_start = read_pos - 1
        words_counted = 0
        while segment_start > 0:
            if text[segment_start] == ' ':
                words_counted += 1
                if words_counted >= words_to_move:
                    segment_start += 1
                    break
            segment_start -= 1

        if segment_start < 0:
            segment_start = 0

        segment_length = read_pos - segment_start
        write_pos -= segment_length
        command_end += 1
        read_pos = command_end + 1 if (command_end < len(text) and text[command_end] == ' ') else command_end

        if move_to_end:
            while read_pos < len(text):
                output_buffer[write_pos] = text[read_pos]
                read_pos += 1
                write_pos += 1

            if write_pos > 0 and output_buffer[write_pos - 1] != ' ':
                output_buffer[write_pos] = ' '
                write_pos += 1

            for offset in range(segment_length):
                output_buffer[write_pos] = text[segment_start + offset]
                write_pos += 1
        else:
            while read_pos < len(text):
                if text[read_pos] == ' ':
                    output_buffer[write_pos] = ' '
                    write_pos += 1
                    for offset in range(segment_length):
                        output_buffer[write_pos] = text[segment_start + offset]
                        write_pos += 1
                    read_pos += 1
                    break

                output_buffer[write_pos] = text[read_pos]
                read_pos += 1
                write_pos += 1
            else:
                if command_end < len(text) and text[command_end] == ' ':
                    output_buffer[write_pos] = ' '
                    write_pos += 1

                for offset in range(segment_length):
                    output_buffer[write_pos] = text[segment_start + offset]
                    write_pos += 1

        made_changes = True

    result = ''.join(output_buffer[:write_pos])
    return shift_words_in_text(result) if made_changes else result

def evaluate_recursive_expressions(text: str) -> str:
    result = text
    position = 0

    while position < len(result):
        is_recursive_eval = (position + 3 < len(result) and
                            result[position] == '@' and
                            result[position + 1] == '(' and
                            result[position + 2] == '@')

        if not is_recursive_eval:
            position += 1
            continue

        def find_matching_closing_paren(search_start: int) -> int:
            search_pos = search_start
            while search_pos < len(result):
                if result[search_pos] == '(':
                    search_pos = find_matching_closing_paren(search_pos + 1)
                    search_pos += 1
                elif result[search_pos] == ')':
                    return search_pos
                else:
                    search_pos += 1
            return search_pos

        closing_paren_pos = find_matching_closing_paren(position + 2)

        if closing_paren_pos >= len(result):
            try:
                closing_paren_pos = result.rindex(')', position)
            except ValueError:
                closing_paren_pos = len(result) - 1

        inner_expression = result[position + 2:closing_paren_pos]
        evaluated_result = eval(inner_expression)
        result = result[:position] + evaluated_result + result[closing_paren_pos + 1:]
        position += len(evaluated_result)

    return result

def eval(text: str) -> str:
    if '@' not in text:
        return text

    text = evaluate_recursive_expressions(text)
    active_flags, text = extract_grammar_flags(text)
    text = apply_conditional_expressions(active_flags, text)
    return shift_words_in_text(text)
