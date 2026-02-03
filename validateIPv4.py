def validate_ipv4_list(ips):
    for ip in ips:
        print(ip)
        if ip is None: 
            print("No IP")
            return False
        if ip == "":
            print("Empty string")
            return False
        if ip == "255.255.255.255":
            print("Broadcast")
            return False
        
        splitted = ip.split(".")
        if len(splitted)!=4:
            print("Not four octects")
            return False
        
        if splitted[0]=="127":
            print("loopback")
            return False
        if "224"<=splitted[0] <="255":
            print("Experimental, or multicast")
            return False
        if splitted[0]=="169" and splitted[1]=="254":
            print("link local address")
            return False
        
        for split in splitted:
            if split == "":
                print("empty octect")
                return False
            if not split.isdigit():
                print("not digit octect")
                return False
            if int(split)>255:
                print("too big octect")
                return False
            if int(split)<0:
                print("negative octect")
                return False
    
    return True
        