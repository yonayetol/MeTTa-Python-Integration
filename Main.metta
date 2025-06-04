!(register-module! ../Training_1)

!(import! &self Training_1:app)

!(import! &self Training_1:data)


(= (write summary of all genes on text) 

    ( let $theWholeData 
        (collapse (match &self (gene $geneCode) 
            (
                    (match &self ($first (gene $geneCode) $last)
                    ($geneCode ---> $first $last))
            )
        ))

        (Summarize_and_write $theWholeData)
    )
)
!(write summary of all genes on text)



