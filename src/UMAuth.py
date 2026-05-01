
 

import hashlib
 
 




class User:
    """
    Base user model with login capability.

    Parameters:
        name: display name of the user
        email: institutional email address
        pwd: plain-text password supplied at login (not stored long-term)
    """
 
    def __init__(self, name, email, pwd):
        self.name = name
        self.email = email

        """
        Store only a SHA-256 hash since you never hold raw passwords in memory
        longer than needed.  The hash is used for local comparison only;
        a real deployment would delegate to the institution's IdP.
        """
        self._pwd_hash = self._hash(pwd)
 


    @staticmethod
    def _hash(raw):
        """
        Returns the SHA-256 hex digest of `raw`.
        Using a static method rather than a module level function keeps the
        hashing logic encapsulated inside the class that needs it and makes
        it easy to swap in bcrypt or argon2 later without touching callers.
        """
        return hashlib.sha256(raw.encode()).hexdigest()
 
 
  
    def usrlogin(self, email, pwd):
        """
        Validates supplied credentials against the stored values.
        Compares hashes rather than raw strings so the plain-text password
        is never directly compared or re-stored
 
        Parameters:
            -email: e-mail address entered by the user on the login screen
            -pwd: password entered by the user on the login screen
 
        Returns:
            bool: True if both email and password are correct, False otherwise.
        """
        email_ok = (email.strip().lower() == self.email.strip().lower())
        pwd_ok   = (self._hash(pwd) == self._pwd_hash)
        return email_ok and pwd_ok
 
 











 
class Administrator(User):
    """
    Elevated-privilege user who can export data, manage RBAC, and enroll
    new faces.
 
    Parameters:

        -name: display name
        -email: institutional e-mail
        -pwd: password (hashed on construction — see User)
    """
 
    def __init__(self, name, email, pwd):
        super().__init__(name, email, pwd)
        # Instance variable — each Administrator has their own flag.
        # Stays False until explicitly granted by a higher-level authority.
        self.is_admin: bool = True

   
   
    def register_face(self, image_path, full_name, faces_folder = "fcs/"):
        """
        Copies or moves a validated face image into the fcs/ directory so
        that FRC will pick it up on next start
        The filename becomes `First Last.png`. Learned that this convention is the same
        one FRC relies on to derive the student's display name from the file
        stem.  Keeping that contract here makes the coupling explicit.
 
        Parameters:

            -image_path:        absolute or relative path to the source image
            -full_name:     "First Last" string (spaces allowed, no path separators)
            -faces_folder:      destination directory — should match FRC's faces_folder
 
        Returns:

            -bool: True on success, False if source file was not found.
        """
        import os
        import shutil
 
        if not os.path.isfile(image_path):
            return False
 
        os.makedirs(faces_folder, exist_ok=True)
        dest = os.path.join(faces_folder, f"{full_name}.png")
        shutil.copy2(image_path, dest)
        return True