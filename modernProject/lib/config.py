from dataclasses import dataclass, field
from typing import Callable, Any, Optional, List, Dict, Tuple, Set


@dataclass
class OutputConf:
    status: Callable[[Any], None]
    header: Callable[[str], None]
    body: Callable[[str], None]
    flush: Callable[[], None]


@dataclass
class Config:
    output_conf: OutputConf
    from_: str = ''
    api_mode: bool = False
    manitou: bool = False
    supervisor: bool = False
    wizard: bool = False
    is_printed_by_template: bool = False
    debug: bool = False
    query_start: float = 0.0
    friend: bool = False
    semi_public: bool = False
    just_friend_wizard: bool = False
    user: str = ''
    username: str = ''
    userkey: str = ''
    user_iper: Optional[int] = None
    command: str = ''
    indep_command: str = ''
    highlight: str = ''
    lang: str = 'en'
    vowels: str = 'aeiouyAEIOUY'
    default_lang: str = 'en'
    browser_lang: str = 'en'
    default_sosa_ref: Optional[Tuple[int, Any]] = None
    multi_parents: bool = False
    authorized_wizards_notes: bool = False
    public_if_titles: bool = False
    public_if_no_date: int = 0
    setup_link: bool = True
    access_by_key: bool = True
    private_years: int = 100
    private_years_death: int = 0
    private_years_marriage: int = 0
    hide_names: bool = False
    use_restrict: bool = False
    no_image: bool = False
    no_note: bool = False
    bname: str = ''
    nb_of_persons: int = 0
    nb_of_families: int = 0
    cgi_passwd: str = ''
    env: Dict[str, str] = field(default_factory=dict)
    senv: Dict[str, str] = field(default_factory=dict)
    henv: Dict[str, str] = field(default_factory=dict)
    base_env: List[Tuple[str, str]] = field(default_factory=list)
    allowed_titles: Set[str] = field(default_factory=set)
    denied_titles: Set[str] = field(default_factory=set)
    request: List[str] = field(default_factory=list)
    lexicon: Dict[str, str] = field(default_factory=dict)
    charset: str = 'UTF-8'
    base_dir: str = '.'
    hide_private_names: bool = False
    cgi: bool = False
