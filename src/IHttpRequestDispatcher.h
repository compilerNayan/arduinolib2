#ifndef I_HTTP_REQUEST_DISPATCHER_H
#define I_HTTP_REQUEST_DISPATCHER_H

#include <StandardDef.h>

DefineStandardPointers(IHttpRequestProcessor)
class IHttpRequestDispatcher {

    Public Virtual ~IHttpRequestProcessor() = default;

    Public Virtual StdString DispatchRequest(IHttpRequestPtr request) = 0;

};

#endif // I_HTTP_REQUEST_DISPATCHER_H