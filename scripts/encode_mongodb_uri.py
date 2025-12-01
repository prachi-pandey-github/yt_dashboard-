"""
MongoDB Connection String Encoder
Helps fix connection string issues with special characters in passwords
"""
from urllib.parse import quote_plus
import re

def encode_mongodb_uri(uri):
    """
    Encode MongoDB URI to handle special characters in username/password
    
    Example:
    Input:  mongodb+srv://user:p@ssw0rd!@cluster.mongodb.net/
    Output: mongodb+srv://user:p%40ssw0rd%21@cluster.mongodb.net/
    """
    try:
        # Check if this is a MongoDB URI
        if "mongodb+srv://" in uri or "mongodb://" in uri:
            # Extract username and password using regex
            pattern = r'mongodb(\+srv)?://([^:]+):([^@]+)@(.+)'
            match = re.match(pattern, uri)
            
            if match:
                protocol = f"mongodb{match.group(1) or ''}"
                username = match.group(2)
                password = match.group(3)
                host_and_params = match.group(4)
                
                print(f"Original URI: {uri}")
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"Host: {host_and_params}")
                
                # URL encode username and password
                encoded_username = quote_plus(username)
                encoded_password = quote_plus(password)
                
                print(f"Encoded username: {encoded_username}")
                print(f"Encoded password: {encoded_password}")
                
                # Reconstruct the URI
                encoded_uri = f"{protocol}://{encoded_username}:{encoded_password}@{host_and_params}"
                print(f"Encoded URI: {encoded_uri}")
                
                return encoded_uri
        
        print("URI doesn't appear to be a MongoDB connection string")
        return uri
        
    except Exception as e:
        print(f"Error encoding URI: {e}")
        return uri

if __name__ == "__main__":
    print("MongoDB Connection String Encoder")
    print("=" * 40)
    
    # Example usage
    example_uri = "mongodb+srv://testuser:p@ssw0rd!@cluster0.xyz.mongodb.net/"
    print("\nExample:")
    encode_mongodb_uri(example_uri)
    
    print("\n" + "=" * 40)
    print("To use:")
    print("1. Get your connection string from MongoDB Atlas")
    print("2. If it contains special characters in password, this script will encode it")
    print("3. Use the encoded version in your Streamlit Cloud secrets")
    print("\nCommon special characters that need encoding:")
    print("@ -> %40")
    print("# -> %23") 
    print("$ -> %24")
    print("% -> %25")
    print("! -> %21")
    print("& -> %26")