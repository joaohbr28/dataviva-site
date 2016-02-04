#sets controler variables for preview of canvas
def templates_preview_controler(bra_id, cnae_id):
    industry = {}
    if bra_id == None :
        industry['flag_preview_headers'] = False
        industry['county'] = True # view county where no country
    else : 
        industry['flag_preview_headers'] = True    
     
        if len(bra_id) == 9 : 
            industry['county'] = False
        else :
            industry['county'] = True    


    if len(cnae_id) == 1 : 
        industry['class'] = True
    else : 
        industry['class'] = False

    if len(cnae_id) == 1 :
        industry['flag_preview_headers'] = False 

    return industry