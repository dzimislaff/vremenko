#/usr/bin/env bash
# https://web.archive.org/web/20200507173259/https://debian-administration.org/article/317/An_introduction_to_bash_completion_part_2

_vreme()
{
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    #
    #  The basic options we'll complete.
    #
    opts="izpis kraji --log --kratko --verzija"

    #
    #  Complete the arguments to some of the basic commands.
    #
    case "${prev}" in
        izpis)
            local running="ljubljana novo-mesto rogaška-slatina metlika \
            dobliče-črnomelj koper-kapitanija bilje-nova-gorica celje idrija \
            ilirska-bistrica kočevje kranj kredarica krško maribor marinča-vas \
            miklavž-na-gorjancih murska-sobota nanos podčetrtek postojna rogla \
            rudno-polje tolmin-volče trbovlje velike-lašče vrhnika"
            COMPREPLY=( $(compgen -W "${running}" -- ${cur}) )
            return 0
            ;;
        kraji)
            local names="-k --kratko"
            COMPREPLY=( $(compgen -W "${names}" -- ${cur}) )
            return 0
            ;;
        *)
        ;;
    esac

   COMPREPLY=($(compgen -W "${opts}" -- ${cur}))  
   return 0

}
complete -F _vreme vreme
