/*
Copyright 2013 NIC Chile Research Labs.
This file is part of PKCS11-TsCrypto.

PKCS11-TsCrypto is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PKCS11-TsCrypto is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PKCS11-TsCrypto.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef TCBHSM_APPLICATION_H
#define TCBHSM_APPLICATION_H

#include "config.h"

#include <vector>
#include <string>
#include <memory>
#include <iosfwd>
#include <dtc.h>

#include "pkcs11.h"
#include "Database.h"

namespace hsm
{
class Slot;
class Session;
class Configuration;

using SlotPtr = std::unique_ptr<Slot>;

/** La aplicacion tiene slots y algunas funcionalidades de ayuda... **/
class Application
{
public:
    Application ( std::ostream& out );
    virtual ~Application();

    virtual Slot & getSlot ( CK_SLOT_ID id ) const; // throws exception
    virtual std::vector<SlotPtr> const & getSlotList() const;

    virtual Slot & getSessionSlot ( CK_SESSION_HANDLE handle );
    virtual Session & getSession ( CK_SESSION_HANDLE session ); // throws exception
    virtual Database & getDatabase ();
    virtual const Configuration & getConfiguration() const;
    virtual dtc_ctx_t * getDtcContext();

    virtual void errorLog ( std::string message ) const;

private:  
    std::ostream& out_;
    Configuration configuration_;
    
    Database database_;

    // An application can have a variable number of slots...
    std::vector<SlotPtr> slots_;

    dtc_ctx_t * dtcCtx_;

};
}

#endif // TCBHSM_APPLICATION_H
