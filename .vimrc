syntax enable
filetype plugin on

set ai

" Automatically insert a closing brace if {<cr> is typed.
inoremap {<cr> {<cr>}<esc>O<tab>

set softtabstop=2
set shiftwidth=2
set autowrite
set incsearch
set confirm
set et

" Turn on line numbering, and set the width to 4 (3 digits).
set nu
set nuw=4
" Turn off paren match highlighting, since it sometimes makes telling where
" the cursor is difficult.
" let loaded_matchparen=1
" Originally =1

" Highlight matching paren
"set showmatch

" Highlight all matches to the most recent search
set hls

" Show tabs and trailing whitespace.
set list
set listchars=tab:\|_,trail:-

" Always show the status bar, and use a particular format.
set laststatus=2
set ruler
set rulerformat=%40(%=%y%m%r\ L%l/%L\ C%c(%v)\ %p%%\ (%P)%)

" set foldmethod=marker

" For dictionary-based word completion.  Type C-x C-k while in insert mode.
if has("unix")
    set dictionary=/usr/share/dict/words
endif

" Manually set encoding to UTF-8 on OS X, since the default locale isn't
" right.
"set encoding=utf-8

" Clear highlighting done by search.
map <silent> \ :let @/=""<cr>
" Toggle search highlighting.
" map <silent> H :set hls!<cr>

highlight Comment ctermfg=black ctermbg=green guifg=black guibg=green

highlight Constant ctermfg=brown guifg=yellow
highlight String ctermfg=brown guifg=yellow
highlight Character ctermfg=brown guifg=yellow
highlight Number ctermfg=brown guifg=yellow
highlight Boolean ctermfg=brown guifg=yellow
highlight Float ctermfg=brown guifg=yellow

highlight Identifier ctermfg=darkcyan guifg=blue
highlight Function ctermfg=darkred guifg=cyan

highlight Statement ctermfg=darkmagenta guifg=magenta
highlight Conditional ctermfg=darkmagenta guifg=magenta
highlight Repeat ctermfg=darkmagenta guifg=magenta
highlight Label ctermfg=darkmagenta guifg=magenta
highlight Operator ctermfg=blue guifg=red
highlight Keyword ctermfg=darkmagenta guifg=magenta
highlight Exception ctermfg=darkmagenta guifg=magenta

highlight PreProc ctermfg=darkmagenta guifg=magenta
highlight Include ctermfg=darkmagenta guifg=magenta
highlight Define ctermfg=darkred guifg=red
highlight Macro ctermfg=darkgreen guifg=green
highlight PreCondit ctermfg=darkred guifg=red

highlight Type ctermfg=darkgreen guifg=green
highlight StorageClass ctermfg=darkgreen guifg=green
highlight Structure ctermfg=darkgreen guifg=green
highlight Typedef ctermfg=darkgreen guifg=green

highlight Special ctermfg=darkmagenta guifg=magenta
highlight SpecialChar ctermfg=darkmagenta guifg=magenta
"Tag
highlight Delimiter ctermfg=darkgreen guifg=green
highlight SpecialComment ctermfg=darkgreen ctermbg=blue guifg=yellow guibg=magenta
"Debug

"Underlined
"Ignore

highlight Error ctermfg=white guifg=white ctermbg=red guibg=red
highlight Todo ctermfg=white guifg=white ctermbg=red guibg=red
highlight ErrorMsg ctermfg=white guifg=white ctermbg=red guibg=red
"MoreMsg
"Question
"WarningMsg
"IncSearch

highlight LineNr ctermfg=darkgreen ctermbg=darkblue guifg=blue guibg=darkblue

highlight Folded ctermfg=grey ctermbg=darkblue guibg=grey guifg=blue

map <C-p> :py3f /usr/share/clang/clang-format-13/clang-format.py<cr>
imap <C-p> <C-o> :py3f /usr/share/clang/clang-format-13/clang-format.py<cr>
