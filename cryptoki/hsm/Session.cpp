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

#include <algorithm>

#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_generators.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <botan/emsa3.h>
#include <botan/emsa4.h>
#include <botan/md5.h>
#include <botan/sha160.h>
#include <botan/sha2_32.h>
#include <botan/sha2_64.h>

#include <sstream>

#include <pkcs11.h>
#include <dtc.h>
#include <iostream>

#include "Session.h"
#include "Slot.h"
#include "Token.h"
#include "CryptoObject.h"
#include "Configuration.h"
#include "TcbError.h"
#include "Application.h"

using namespace hsm;
using namespace std;

namespace {

    bool userAuthorization(CK_STATE sessionState, CK_BBOOL isTokenObject,
                           CK_BBOOL isPrivateObject, bool userAction) {
        switch (sessionState) {
            case CKS_RW_SO_FUNCTIONS:
                return isPrivateObject == CK_FALSE;
                break;

            case CKS_RW_USER_FUNCTIONS:
                return true;
                break;

            case CKS_RO_USER_FUNCTIONS:
                if (isTokenObject == CK_TRUE) {
                    return !userAction; // Es más explicito así
                } else {
                    return true;
                }
                break;

            case CKS_RW_PUBLIC_SESSION:
                return isPrivateObject == CK_FALSE;
                break;

            case CKS_RO_PUBLIC_SESSION:
                if (isPrivateObject == CK_FALSE) {
                    return (isTokenObject != CK_TRUE) || !userAction;
                } else {
                    return false;
                }
                break;

            default:
                break;
        }

        return false;
    }

    CK_SESSION_HANDLE actualHandle = 0;

}

Session::Session(CK_FLAGS flags, CK_VOID_PTR pApplication,
                 CK_NOTIFY notify, Slot &currentSlot)
        : handle_(++actualHandle), flags_(flags), application_(pApplication), notify_(notify), slot_(currentSlot) {
    // TODO: Set Uuid
}

Session::~Session() {

    Token &token = slot_.getToken();
    auto &objects = token.getObjects();

    for (auto &objectPair: objects) {
        CryptoObject &object = *(objectPair.second);

        if (object.getType() == CryptoObjectType::SESSION_OBJECT) {

            CK_ATTRIBUTE tmpl = {.type=CKA_VENDOR_DEFINED};
            CK_ATTRIBUTE const *handlerAttribute = object.findAttribute(&tmpl);
            if (handlerAttribute != nullptr) {

                // If a keypair is stored, then each the public and the private key
                // will be deleted.
                // Neitherless if it's only one instance stored in the backend.
                char *value = static_cast<char *> ( handlerAttribute->pValue );
                string handler(value, handlerAttribute->ulValueLen);
                // TODO: Delete Key
            }

            objects.erase(objectPair.first);
        }
    }
}

const string &Session::getUuid() {
    return uuid_;
}

CK_SESSION_HANDLE Session::getHandle() const {
    return handle_;
}

Slot &Session::getCurrentSlot() {
    return slot_;
}

void Session::getSessionInfo(CK_SESSION_INFO_PTR pInfo) const {
    if (pInfo != nullptr) {
        pInfo->slotID = slot_.getId();
        pInfo->state = getState();
        pInfo->flags = getFlags();
        pInfo->ulDeviceError = 0;
    } else {
        throw TcbError("Session::getSessionInfo", "pInfo == nullptr", CKR_ARGUMENTS_BAD);
    }
}

CK_OBJECT_HANDLE Session::createObject(CK_ATTRIBUTE_PTR pTemplate, CK_ULONG ulCount) {
    if (pTemplate == nullptr) {
        throw TcbError("Session::createObject", "pTemplate es nullptr.", CKR_ARGUMENTS_BAD);
    }

    // Original from SoftHSM...
    CK_BBOOL isToken = CK_FALSE;
    CK_BBOOL isPrivate = CK_TRUE;
    CK_OBJECT_CLASS oClass = CKO_VENDOR_DEFINED;
    CK_KEY_TYPE keyType = CKK_VENDOR_DEFINED;

    // Extract object information
    for (CK_ULONG i = 0; i < ulCount; i++) {
        switch (pTemplate[i].type) {
            case CKA_TOKEN:
                if (pTemplate[i].ulValueLen == sizeof(CK_BBOOL)) {
                    isToken = *(CK_BBOOL *) pTemplate[i].pValue;
                }
                break;

            case CKA_PRIVATE:
                if (pTemplate[i].ulValueLen == sizeof(CK_BBOOL)) {
                    isPrivate = *(CK_BBOOL *) pTemplate[i].pValue;
                }
                break;

            case CKA_CLASS:
                if (pTemplate[i].ulValueLen == sizeof(CK_OBJECT_CLASS)) {
                    oClass = *(CK_OBJECT_CLASS *) pTemplate[i].pValue;
                }
                break;

            case CKA_KEY_TYPE:
                if (pTemplate[i].ulValueLen == sizeof(CK_KEY_TYPE)) {
                    keyType = *(CK_KEY_TYPE *) pTemplate[i].pValue;
                }
                break;
            default:
                break;
        }
    }

    if (isToken == CK_TRUE && this->isReadOnly()) {
        throw TcbError("Session::createObject", "isToken == CK_TRUE && this->isReadOnly()", CKR_SESSION_READ_ONLY);
    }

    if (!userAuthorization(getState(), isToken, isPrivate, true))
        throw TcbError("Session::createObject",
                       "!userAuthorization(getState(), isToken, isPrivate, true)",
                       CKR_USER_NOT_LOGGED_IN);

    switch (oClass) {
        case CKO_PUBLIC_KEY:
        case CKO_PRIVATE_KEY:
            if (keyType == CKK_RSA) {
                Token &token = slot_.getToken();
                CryptoObjectType objectType =
                        isToken ?
                        CryptoObjectType::TOKEN_OBJECT :
                        CryptoObjectType::SESSION_OBJECT;

                CryptoObject *object = new CryptoObject(pTemplate, ulCount, objectType);

                CK_OBJECT_HANDLE handle = token.addObject(object);
                // Update the database
                // TODO: reorder this...
                getCurrentSlot().getApplication().getDatabase().saveToken(token);
                return handle;
            } else {
                throw TcbError("Session::createObject",
                               "keyType != CKK_RSA",
                               CKR_ATTRIBUTE_VALUE_INVALID);
            }
        default:
            throw TcbError("Session::createObject",
                           "La clase del objeto no está soportada.",
                           CKR_ATTRIBUTE_VALUE_INVALID);
    }

    // TODO: Verificar que los objetos sean validos.
}

void Session::destroyObject(CK_OBJECT_HANDLE hObject) {
    Token &token = slot_.getToken();
    auto &objectContainer = token.getObjects();

    auto it = objectContainer.find(hObject);
    if (it != objectContainer.end()) {

        // Verifico que el objeto no sea una llave, y si lo es, la elimino del TCB.
        CK_ATTRIBUTE tmpl = {.type=CKA_VENDOR_DEFINED};
        const CK_ATTRIBUTE *handlerAttribute = it->second->findAttribute(&tmpl);
        if (handlerAttribute != nullptr) {
            string handler((char *) handlerAttribute->pValue,
                           handlerAttribute->ulValueLen);
            // TODO: Delete Key

        }

        objectContainer.erase(it);
        getCurrentSlot().getApplication().getDatabase().saveToken(token);
    } else {
        throw TcbError("Session::destroyObject", "Objeto no encontrado.", CKR_OBJECT_HANDLE_INVALID);
    }
}

void Session::findObjectsInit(CK_ATTRIBUTE_PTR pTemplate, CK_ULONG ulCount) {
    // TODO: Verificar correctitud
    if (findInitialized_) {
        throw TcbError("Session::findObjectsInit", "findInitialized", CKR_OPERATION_ACTIVE);
    }
    if (pTemplate == nullptr) {
        throw TcbError("Session::findObjectsInit", "pTemplate == nullptr", CKR_ARGUMENTS_BAD);
    }

    Token &token = slot_.getToken();

    if (ulCount == 0) {
        // Busco todos los objetos...
        for (auto &handleObjectPair: token.getObjects()) {
            foundObjects_.push_back(handleObjectPair.first);
        }
    } else {
        for (auto &handleObjectPair: token.getObjects()) {
            if (handleObjectPair.second->match(pTemplate, ulCount)) {
                foundObjects_.push_back(handleObjectPair.first);
            }
        }
    }

    //TODO: verificar permisos de acceso.
    foundObjectsIterator_ = foundObjects_.begin();
    foundObjectsEnd_ = foundObjects_.end();
    findInitialized_ = true;
}

vector<CK_OBJECT_HANDLE> Session::findObjects(CK_ULONG maxObjectCount) {
    if (!findInitialized_) {
        throw TcbError("Session::findObjects",
                       "No se inicio la busqueda.",
                       CKR_OPERATION_NOT_INITIALIZED);
    }

    auto end = foundObjectsIterator_ + maxObjectCount;
    if (foundObjectsEnd_ < end) {
        end = foundObjectsEnd_;
    }

    vector<CK_OBJECT_HANDLE> response(foundObjectsIterator_, end);
    foundObjectsIterator_ = end;
    return response;
}

void Session::findObjectsFinal() {
    if (!findInitialized_) {
        throw TcbError("Session::findObjects", "No se inicio la busqueda.",
                       CKR_OPERATION_NOT_INITIALIZED);
    } else {
        findInitialized_ = false;
    }
}


CryptoObject &Session::getObject(CK_OBJECT_HANDLE objectHandle) {
    try {
        return slot_.getToken().getObject(objectHandle);
    } catch (std::out_of_range &e) {
        throw TcbError("Session::getObject", "Objeto no existe en la sesion.", CKR_OBJECT_HANDLE_INVALID);
    }
}


CK_STATE Session::getState() const {
    // TODO: Completar la semántica de lecto-escritura.
    switch (slot_.getToken().getSecurityLevel()) {
        case Token::SecurityLevel::SECURITY_OFFICER:
            return CKS_RW_SO_FUNCTIONS;
        case Token::SecurityLevel::USER:
            if (isReadOnly()) {
                return CKS_RO_USER_FUNCTIONS;
            } else {
                return CKS_RW_USER_FUNCTIONS;
            }
        case Token::SecurityLevel::PUBLIC:
            if (isReadOnly()) {
                return CKS_RO_PUBLIC_SESSION;
            } else {
                return CKS_RW_PUBLIC_SESSION;
            }
    }
}

bool Session::isReadOnly() const {
    return (flags_ & CKF_RW_SESSION) != CKF_RW_SESSION;
}

CK_FLAGS Session::getFlags() const {
    return flags_;
}

void Session::login(CK_USER_TYPE userType, CK_UTF8CHAR_PTR pPin, CK_ULONG ulPinLen) {
    Token &token = slot_.getToken();
    token.login(userType, pPin, ulPinLen);
}

void Session::logout() {
    slot_.getToken().logout();
}

namespace {
    CK_OBJECT_HANDLE createPublicKey(Session &session,
                                     CK_ATTRIBUTE_PTR pPublicKeyTemplate,
                                     CK_ULONG ulPublicKeyAttributeCount,
                                     const string &rabbitHandler,
                                     const string &metainfo,
                                     const bytes_t *modulus,
                                     const bytes_t *publicExponent
    ) {
        // NOTE: This comes in some way from SoftHSM...
        CK_OBJECT_CLASS oClass = CKO_PUBLIC_KEY;
        CK_KEY_TYPE keyType = CKK_RSA;
        CK_MECHANISM_TYPE mechType = CKM_RSA_PKCS_KEY_PAIR_GEN;
        CK_BBOOL ckTrue = CK_TRUE, ckFalse = CK_FALSE;
        CK_DATE emptyDate;

        // Generic attributes...
        CK_ATTRIBUTE aClass = {CKA_CLASS, &oClass, sizeof(oClass)};
        CK_ATTRIBUTE aKeyType = {CKA_KEY_TYPE, &keyType, sizeof(keyType)};
        CK_ATTRIBUTE aMechType = {CKA_KEY_GEN_MECHANISM, &mechType, sizeof(mechType)};
        CK_ATTRIBUTE aLocal = {CKA_LOCAL, &ckTrue, sizeof(ckTrue)};

        CK_ATTRIBUTE aLabel = {CKA_LABEL, NULL_PTR, 0};
        CK_ATTRIBUTE aId = {CKA_ID, NULL_PTR, 0};
        CK_ATTRIBUTE aSubject = {CKA_SUBJECT, NULL_PTR, 0};
        CK_ATTRIBUTE aPrivate = {CKA_PRIVATE, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aModifiable = {CKA_MODIFIABLE, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aToken = {CKA_TOKEN, &ckFalse, sizeof(ckFalse)};
        CK_ATTRIBUTE aDerive = {CKA_DERIVE, &ckFalse, sizeof(ckFalse)};
        CK_ATTRIBUTE aEncrypt = {CKA_ENCRYPT, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aVerify = {CKA_VERIFY, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aVerifyRecover = {CKA_VERIFY_RECOVER, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aWrap = {CKA_WRAP, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aTrusted = {CKA_TRUSTED, &ckFalse, sizeof(ckFalse)};
        CK_ATTRIBUTE aStartDate = {CKA_START_DATE, &emptyDate, 0};
        CK_ATTRIBUTE aEndDate = {CKA_END_DATE, &emptyDate, 0};
        CK_ATTRIBUTE aModulusBits = {CKA_MODULUS_BITS, NULL_PTR, 0};

        // NOTE: CKA_VENDOR_DEFINED = CKA_RABBIT_HANDLER.
        CK_ATTRIBUTE aValue = {
                .type=CKA_VENDOR_DEFINED,
                .pValue= (void *) rabbitHandler.c_str(),
                .ulValueLen=rabbitHandler.size()
        };

        CK_ATTRIBUTE aMetainfo = {
                .type=CKA_VENDOR_DEFINED+1,
                .pValue= (void*) metainfo.c_str(),
                .ulValueLen=metainfo.size()
        };

        CK_ATTRIBUTE aModulus = {
                .type = CKA_MODULUS,
                .pValue = modulus->data,
                .ulValueLen = modulus->data_len
        };

        CK_ATTRIBUTE aExponent = {
                .type = CKA_PUBLIC_EXPONENT,
                .pValue = publicExponent->data,
                .ulValueLen = publicExponent->data_len
        };

        for (CK_ULONG i = 0; i < ulPublicKeyAttributeCount; i++) {
            switch (pPublicKeyTemplate[i].type) {
                case CKA_LABEL:
                    aLabel = pPublicKeyTemplate[i];
                    break;
                case CKA_ID:
                    aId = pPublicKeyTemplate[i];
                    break;
                case CKA_SUBJECT:
                    aSubject = pPublicKeyTemplate[i];
                    break;
                case CKA_DERIVE:
                    aDerive = pPublicKeyTemplate[i];
                    break;
                case CKA_TOKEN:
                    aToken = pPublicKeyTemplate[i];
                    break;
                case CKA_PRIVATE:
                    aPrivate = pPublicKeyTemplate[i];
                    break;
                case CKA_MODIFIABLE:
                    aModifiable = pPublicKeyTemplate[i];
                    break;
                case CKA_ENCRYPT:
                    aEncrypt = pPublicKeyTemplate[i];
                    break;
                case CKA_VERIFY:
                    aVerify = pPublicKeyTemplate[i];
                    break;
                case CKA_VERIFY_RECOVER:
                    aVerifyRecover = pPublicKeyTemplate[i];
                    break;
                case CKA_WRAP:
                    aWrap = pPublicKeyTemplate[i];
                    break;
                case CKA_TRUSTED:
                    aSubject = pPublicKeyTemplate[i];
                    break;
                case CKA_START_DATE:
                    aStartDate = pPublicKeyTemplate[i];
                    break;
                case CKA_END_DATE:
                    aEndDate = pPublicKeyTemplate[i];
                    break;
                case CKA_MODULUS_BITS:
                    aModulusBits = pPublicKeyTemplate[i];
                    break;
                default:
                    break;
            }
        }

        CK_ATTRIBUTE attributes[] = {
                aClass,
                aKeyType,
                aMechType,
                aLocal,
                aLabel,
                aId,
                aSubject,
                aPrivate,
                aModifiable,
                aToken,
                aDerive,
                aEncrypt,
                aVerify,
                aVerifyRecover,
                aWrap,
                aTrusted,
                aStartDate,
                aEndDate,
                aValue,
                aMetainfo,
                aModulus,
                aExponent
        };

        return session.createObject(attributes, sizeof(attributes) / sizeof(attributes[0]));
    }

    CK_OBJECT_HANDLE createPrivateKey(Session &session,
                                      CK_ATTRIBUTE_PTR pPrivateKeyTemplate,
                                      CK_ULONG ulPrivateKeyAttributeCount,
                                      string const &keyHandler,
                                      const string &metainfo,
                                      const bytes_t *modulus,
                                      const bytes_t *publicExponent
    ) {
        CK_OBJECT_CLASS oClass = CKO_PRIVATE_KEY;
        CK_KEY_TYPE keyType = CKK_RSA;
        CK_MECHANISM_TYPE mechType = CKM_RSA_PKCS_KEY_PAIR_GEN;
        CK_BBOOL ckTrue = CK_TRUE, ckFalse = CK_FALSE;
        CK_DATE emptyDate;

        // Generic attributes...
        CK_ATTRIBUTE aClass = {CKA_CLASS, &oClass, sizeof(oClass)};
        CK_ATTRIBUTE aKeyType = {CKA_KEY_TYPE, &keyType, sizeof(keyType)};
        CK_ATTRIBUTE aMechType = {CKA_KEY_GEN_MECHANISM, &mechType, sizeof(mechType)};
        CK_ATTRIBUTE aLocal = {CKA_LOCAL, &ckTrue, sizeof(ckTrue)};

        CK_ATTRIBUTE aLabel = {CKA_LABEL, NULL_PTR, 0};
        CK_ATTRIBUTE aId = {CKA_ID, NULL_PTR, 0};
        CK_ATTRIBUTE aSubject = {CKA_SUBJECT, NULL_PTR, 0};
        CK_ATTRIBUTE aPrivate = {CKA_PRIVATE, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aModifiable = {CKA_MODIFIABLE, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aToken = {CKA_TOKEN, &ckFalse, sizeof(ckFalse)};
        CK_ATTRIBUTE aDerive = {CKA_DERIVE, &ckFalse, sizeof(ckFalse)};

        CK_ATTRIBUTE aWrapWithTrusted = {CKA_WRAP_WITH_TRUSTED, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aAlwaysAuthenticate = {CKA_ALWAYS_AUTHENTICATE, &ckFalse, sizeof(ckFalse)};
        CK_ATTRIBUTE aSensitive = {CKA_SENSITIVE, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aAlwaysSensitive = {CKA_ALWAYS_SENSITIVE, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aDecrypt = {CKA_DECRYPT, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aSign = {CKA_SIGN, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aSignRecover = {CKA_SIGN_RECOVER, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aUnwrap = {CKA_UNWRAP, &ckTrue, sizeof(ckTrue)};
        CK_ATTRIBUTE aExtractable = {CKA_EXTRACTABLE, &ckFalse, sizeof(ckFalse)};
        CK_ATTRIBUTE aNeverExtractable = {CKA_NEVER_EXTRACTABLE, &ckTrue, sizeof(ckTrue)};

        CK_ATTRIBUTE aStartDate = {CKA_START_DATE, &emptyDate, 0};
        CK_ATTRIBUTE aEndDate = {CKA_END_DATE, &emptyDate, 0};


        // NOTE: CKA_VENDOR_DEFINED = CKA_RABBIT_HANDLER.
        CK_ATTRIBUTE aValue = {
                .type=CKA_VENDOR_DEFINED,
                .pValue= (void *) keyHandler.c_str(),
                .ulValueLen = keyHandler.size()
        };

        CK_ATTRIBUTE aMetainfo = {
                .type=CKA_VENDOR_DEFINED+1,
                .pValue= (void*) metainfo.c_str(),
                .ulValueLen=metainfo.size()
        };

        CK_ATTRIBUTE aModulus = {
                .type = CKA_MODULUS,
                .pValue = (void *) modulus->data,
                .ulValueLen = modulus->data_len
        };

        CK_ATTRIBUTE aExponent = {
                .type = CKA_PUBLIC_EXPONENT,
                .pValue = (void *) publicExponent->data,
                .ulValueLen = publicExponent->data_len
        };

        for (CK_ULONG i = 0; i < ulPrivateKeyAttributeCount; i++) {
            switch (pPrivateKeyTemplate[i].type) {
                case CKA_LABEL:
                    aLabel = pPrivateKeyTemplate[i];
                    break;
                case CKA_ID:
                    aId = pPrivateKeyTemplate[i];
                    break;
                case CKA_SUBJECT:
                    aSubject = pPrivateKeyTemplate[i];
                    break;
                case CKA_TOKEN:
                    aToken = pPrivateKeyTemplate[i];
                    break;
                case CKA_PRIVATE:
                    aPrivate = pPrivateKeyTemplate[i];
                    break;
                case CKA_DERIVE:
                    aDerive = pPrivateKeyTemplate[i];
                    break;
                case CKA_MODIFIABLE:
                    aModifiable = pPrivateKeyTemplate[i];
                    break;
                case CKA_DECRYPT:
                    aDecrypt = pPrivateKeyTemplate[i];
                    break;
                case CKA_SIGN:
                    aSign = pPrivateKeyTemplate[i];
                    break;
                case CKA_SIGN_RECOVER:
                    aSignRecover = pPrivateKeyTemplate[i];
                    break;
                case CKA_UNWRAP:
                    aUnwrap = pPrivateKeyTemplate[i];
                    break;
                case CKA_WRAP_WITH_TRUSTED:
                    aWrapWithTrusted = pPrivateKeyTemplate[i];
                    break;
                case CKA_ALWAYS_AUTHENTICATE:
                    aAlwaysAuthenticate = pPrivateKeyTemplate[i];
                    break;
                case CKA_START_DATE:
                    aStartDate = pPrivateKeyTemplate[i];
                    break;
                case CKA_END_DATE:
                    aEndDate = pPrivateKeyTemplate[i];
                    break;
                default:
                    break;
            }
        }

        CK_ATTRIBUTE attributes[] = {
                aClass,
                aKeyType,
                aMechType,
                aLocal,

                aLabel,
                aId,
                aSubject,
                aPrivate,
                aModifiable,
                aToken,
                aDerive,
                aWrapWithTrusted,
                aAlwaysAuthenticate,
                aSensitive,
                aAlwaysSensitive,
                aDecrypt,
                aSign,
                aSignRecover,
                aUnwrap,
                aExtractable,
                aNeverExtractable,
                aValue,
                aMetainfo,
                aModulus,
                aExponent,

                aStartDate,
                aEndDate
        };

        return session.createObject(attributes, sizeof(attributes) / sizeof(attributes[0]));
    }

}

KeyPair Session::generateKeyPair(CK_MECHANISM_PTR pMechanism,
                                 CK_ATTRIBUTE_PTR pPublicKeyTemplate, CK_ULONG ulPublicKeyAttributeCount,
                                 CK_ATTRIBUTE_PTR pPrivateKeyTemplate, CK_ULONG ulPrivateKeyAttributeCount) {
    // TODO: verificar permisos de acceso.
    if (pMechanism == nullptr || pPublicKeyTemplate == nullptr || pPrivateKeyTemplate == nullptr) {
        throw TcbError("Session::generateKeyPair", "Argumentos nulos", CKR_ARGUMENTS_BAD);
    }

    // Se extrae la información relevante para crear la llave.
    CK_ULONG modulusBits = 0;
    // string exponent = "";

    for (CK_ULONG i = 0; i < ulPublicKeyAttributeCount; i++) {
        switch (pPublicKeyTemplate[i].type) {
            case CKA_MODULUS_BITS: {
                if (pPublicKeyTemplate[i].ulValueLen != sizeof(CK_ULONG)) {
                    throw TcbError("Session::generateKeyPair", "pPublicKeyTemplate[i].ulValueLen != sizeof(CK_ULONG)",
                                   CKR_TEMPLATE_INCOMPLETE);
                }
                modulusBits = *static_cast<CK_ULONG *> ( pPublicKeyTemplate[i].pValue );
            }
                break;
            case CKA_PUBLIC_EXPONENT: {
                // TODO: Set Exponent (Discard Exponent?)
            }
                break;
            default:
                break;
        }
    }

    if (modulusBits == 0) {
        throw TcbError("Session::generateKeyPair", "modulusBits == \"\"", CKR_TEMPLATE_INCOMPLETE);
    }

    switch (pMechanism->mechanism) {
        // case CKM_VENDOR_DEFINED:
        case CKM_RSA_PKCS_KEY_PAIR_GEN:
            // RSA is the only accepted method...
            boost::uuids::random_generator uuidGen;
            string keyHandler = to_string(uuidGen());
            // Todo: check if generated uuid is already taken.

            Application &app = getCurrentSlot().getApplication();
            dtc_ctx_t *ctx = app.getDtcContext();
            const Configuration &cfg = app.getConfiguration();

            key_metainfo_t *metainfo;
            int err = dtc_generate_key_shares(ctx, keyHandler.c_str(), modulusBits, cfg.getThreshold(),
                                              cfg.getNodesNumber(), &metainfo);
            if (err != DTC_ERR_NONE) {
                throw TcbError("Session::generateKeyPair", std::string(dtc_get_error_msg(err)), CKR_GENERAL_ERROR);
            }

            string serializedMetainfo(tc_serialize_key_metainfo(metainfo));
            std::cout << "Metainfo 1: " << serializedMetainfo << std::endl;

            const public_key_t *pk = tc_key_meta_info_public_key(metainfo);

            const bytes_t *n = tc_public_key_n(pk);
            const bytes_t *e = tc_public_key_e(pk);

            CK_OBJECT_HANDLE publicKeyHandle = createPublicKey(*this, pPublicKeyTemplate,
                                                               ulPublicKeyAttributeCount,
                                                               keyHandler,
                                                               serializedMetainfo,
                                                               n,
                                                               e);
            CK_OBJECT_HANDLE privateKeyHandle = createPrivateKey(*this, pPrivateKeyTemplate,
                                                                 ulPrivateKeyAttributeCount,
                                                                 keyHandler,
                                                                 serializedMetainfo,
                                                                 n,
                                                                 e);
            return KeyPair {privateKeyHandle, publicKeyHandle};
    }

    throw TcbError("Session::generateKeyPair", "Mechanism invalid.", CKR_MECHANISM_INVALID);

}

void Session::signInit(CK_MECHANISM_PTR pMechanism, CK_OBJECT_HANDLE hKey) {
    CryptoObject &keyObject = getObject(hKey);
    CK_ATTRIBUTE tmpl = {.type = CKA_VENDOR_DEFINED};

    const CK_ATTRIBUTE *keyName = keyObject.findAttribute(&tmpl);
    if (!keyName) {
        throw TcbError("Session::signInit", "El object handle no contiene ninguna llave", CKR_ARGUMENTS_BAD);
    }

    tmpl = {.type = CKA_VENDOR_DEFINED + 1};
    const CK_ATTRIBUTE *keyMetainfoAttribute = keyObject.findAttribute(&tmpl);
    if (!keyMetainfoAttribute) {
        throw TcbError("Session::signInit", "El object handle no contiene keymetainfos", CKR_ARGUMENTS_BAD);
    }

    string metainfo(static_cast<char*>(keyMetainfoAttribute->pValue), keyMetainfoAttribute->ulValueLen);
    string keyHandler(static_cast<char*>(keyName->pValue), keyName->ulValueLen);
    signMechanism_ = pMechanism->mechanism;
    signHandler_ = keyHandler;

    std::cout << "Metainfo 2: " << metainfo << std::endl;
    keyMetainfo_ = tc_deserialize_key_metainfo(metainfo.c_str());

    signInitialized_ = true;
}

void Session::sign(CK_BYTE_PTR pData, CK_ULONG ulDataLen, CK_BYTE_PTR pSignature, CK_ULONG_PTR pulSignatureLen) {

    if (!signInitialized_) {
        throw TcbError("Session::sign", "Operation not initialized.", CKR_OPERATION_NOT_INITIALIZED);
    }

    try {

        Botan::EMSA *padder;
        Botan::HashFunction *hasher;

        // First hasher
        switch (signMechanism_) {
            case CKM_RSA_PKCS:
                hasher = nullptr;
                break;

            case CKM_MD5_RSA_PKCS:
                hasher = new Botan::MD5;
                break;

            case CKM_SHA1_RSA_PKCS:
            case CKM_SHA1_RSA_PKCS_PSS:
                hasher = new Botan::SHA_160;
                break;

            case CKM_SHA256_RSA_PKCS:
            case CKM_SHA256_RSA_PKCS_PSS:
                hasher = new Botan::SHA_256;
                break;

            case CKM_SHA384_RSA_PKCS:
            case CKM_SHA384_RSA_PKCS_PSS:
                hasher = new Botan::SHA_384;
                break;

            case CKM_SHA512_RSA_PKCS:
            case CKM_SHA512_RSA_PKCS_PSS:
                hasher = new Botan::SHA_512;
                break;

            default:
                throw TcbError("Session::sign", "El mecanismo no esta soportado.", CKR_MECHANISM_INVALID);
        }

        // Then padder
        switch (signMechanism_) {
            case CKM_RSA_PKCS:
                padder = new Botan::EMSA3_Raw;
                break;

            case CKM_MD5_RSA_PKCS:
            case CKM_SHA1_RSA_PKCS:
            case CKM_SHA256_RSA_PKCS:
            case CKM_SHA384_RSA_PKCS:
            case CKM_SHA512_RSA_PKCS:
                padder = new Botan::EMSA3(hasher);
                break;

            case CKM_SHA1_RSA_PKCS_PSS:
            case CKM_SHA256_RSA_PKCS_PSS:
            case CKM_SHA384_RSA_PKCS_PSS:
            case CKM_SHA512_RSA_PKCS_PSS:
                padder = new Botan::EMSA4(hasher);
                break;

            default:
                throw TcbError("Session::sign", "El mecanismo no esta soportado.", CKR_MECHANISM_INVALID);
        }

        padder->update(pData, ulDataLen);
        auto paddedData = padder->raw_data();
        auto paddedDataBytes = tc_init_bytes(paddedData, paddedData.size());

        dtc_ctx_t *ctx = getCurrentSlot().getApplication().getDtcContext();

        bytes_t *signature;
        std::cout << "signHandler: " << signHandler_ <<std::endl;
        int sign_err = dtc_sign(ctx, keyMetainfo_, signHandler_.c_str(), paddedDataBytes, &signature);
        if (sign_err != DTC_ERR_NONE) {
            throw TcbError("Session::sign", dtc_get_error_msg(sign_err), CKR_GENERAL_ERROR);
        }

        if (*pulSignatureLen < signature->data_len) {

            throw TcbError("Session::sign", "Buffer too small.", CKR_BUFFER_TOO_SMALL);
        }
        *pulSignatureLen = signature->data_len;

        CK_BYTE_PTR data = (CK_BYTE_PTR) signature->data;
        uint32_t dataLen = signature->data_len;
        std::copy(data, data + dataLen, pSignature);

        signInitialized_ = false;
    } catch (TcbError &e) {
        throw e;
    } catch (std::exception &e) {
        throw TcbError("Session::sign", e.what(), CKR_GENERAL_ERROR);
    }
}

void Session::digestInit(CK_MECHANISM_PTR pMechanism) {
    if (digestInitialized_) {
        throw TcbError("Session::digestInit", "Operation active.", CKR_OPERATION_ACTIVE);
    }

    if (pMechanism == nullptr) {
        throw TcbError("Session::digestInit", "pMechanism == nullptr.", CKR_ARGUMENTS_BAD);
    }

    string mechanism;
    CK_ULONG mechSize = 0;
    switch (pMechanism->mechanism) {
        case CKM_MD5:
            mechSize = 16;
            mechanism = "MD5";
            break;
            //       case CKM_RIPEMD160:
            //         mechSize = 20;
            //         hashFunc = new Botan::RIPEMD_160;
            //         break;
        case CKM_SHA_1:
            mechSize = 20;
            mechanism = "SHA1";
            break;
        case CKM_SHA256:
            mechSize = 32;
            mechanism = "SHA256";
            break;
        case CKM_SHA384:
            mechSize = 48;
            mechanism = "SHA384";
            break;
        case CKM_SHA512:
            mechSize = 64;
            mechanism = "SHA512";
            break;
        default:
            throw TcbError("Session::digestInit", "mechanism invalid.", CKR_MECHANISM_INVALID);
            break;
    }

    // TODO: Digest Initialization

    digestInitialized_ = true;
    digestSize_ = mechSize;
}

void Session::digest(CK_BYTE_PTR pData, CK_ULONG ulDataLen, CK_BYTE_PTR pDigest, CK_ULONG_PTR pulDigestLen) {
    if (!digestInitialized_) {
        throw TcbError("Session::digest", "Operation not initialized.", CKR_OPERATION_NOT_INITIALIZED);
    }

    if (pulDigestLen == nullptr) {
        throw TcbError("Session::digest", "pulDigestLen == nulllptr", CKR_ARGUMENTS_BAD);
    }

    if (pDigest == nullptr) {
        *pulDigestLen = digestSize_;
        return;
    }

    if (*pulDigestLen < digestSize_) {
        *pulDigestLen = digestSize_;
        throw TcbError("Session::digest", "buffer too small.", CKR_BUFFER_TOO_SMALL);
    }

    if (pData == nullptr) {
        throw TcbError("Session::digest", "pData == nullptr", CKR_ARGUMENTS_BAD);
    }

    // TODO: Digest generation
    vector<CK_BYTE> digest; // ( base64::decode ( encodedDigest ) );
    // unsigned long size = digest.size();
    *pulDigestLen = digestSize_;

    CK_BYTE_PTR data = digest.data();
    std::copy(data, data + *pulDigestLen, pDigest);
    digestInitialized_ = false;
    digestSize_ = 0;
}

void Session::generateRandom(CK_BYTE_PTR pRandomData, CK_ULONG ulRandomLen) {
    if (pRandomData == nullptr) {
        throw TcbError("Session::generateRandom", "pRandomData == nullptr", CKR_ARGUMENTS_BAD);
    }

    // TODO: Random bytes generation

    vector<CK_BYTE> decodedData;//  ( base64::decode ( encodedData ) );
    CK_BYTE_PTR data = decodedData.data();

    std::copy(data, data + ulRandomLen, pRandomData);
}

void Session::seedRandom(CK_BYTE_PTR pSeed, CK_ULONG ulSeedLen) {
    if (pSeed == nullptr) {
        throw TcbError("Session::seedRandom", "pSeed == nullptr", CKR_ARGUMENTS_BAD);
    }

    // TODO: Random seed.
}

