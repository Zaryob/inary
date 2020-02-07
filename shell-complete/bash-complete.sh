_inary() 
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="ar bl bi check cm cp dc dt dr em emup er fc graph hs ix info it la lc li ln ln lp lr lu rdb rp ro rr sr sf ur up"

    if [[ ${cur} == * ]] && [ ${prev} == inary ] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    fi
    if [[ ${cur} == * ]] && [ ${prev} == it ] ; then
        avaiable=$(cat /var/cache/inary/avaiable)
        COMPREPLY=( $(compgen -W "${avaiable}" -- ${cur}) )
    fi
    if [[ ${cur} == * ]] && [ ${prev} == rm ] ; then
        avaiable=$(cat /var/cache/inary/installed)
        COMPREPLY=( $(compgen -W "${avaiable}" -- ${cur}) )
    fi
   if [[ ${cur} == * ]] && [ ${prev} == rr ] ; then
        avaiable=$(cat /var/cache/inary/repos)
        COMPREPLY=( $(compgen -W "${avaiable}" -- ${cur}) )
    fi
}
complete -F _inary inary
