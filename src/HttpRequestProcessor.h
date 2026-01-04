#ifndef HTTP_REQUEST_PROCESSOR_H
#define HTTP_REQUEST_PROCESSOR_H

#include "IHttpRequestProcessor.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestDispatcher.h"
#include <ServerFactory.h>

/// @Component
class HttpRequestProcessor final : public IHttpRequestProcessor {

    /// @Autowired
    Private IHttpRequestQueuePtr requestQueue;

    /// @Autowired
    Private IHttpRequestDispatcherPtr dispatcher;

    Private IServerPtr server;

    Public HttpRequestProcessor() : server(ServerFactory::GetDefaultServer()) {
    }

    Public ~HttpRequestProcessor() override = default;

    // ============================================================================
    // HTTP Request Processing Operations
    // ============================================================================
    
    Public Bool ProcessRequest() override {
        if (requestQueue->IsEmpty()) {
            return false;
        }
        
        IHttpRequestPtr request = requestQueue->DequeueRequest();
        if (request == nullptr) {
            return false;
        }
        
        Val response = dispatcher->DispatchRequest(request);
        if (response.length() > 0) {
            server->SendMessage(request->GetRequestId(), response);
        }
        return true;
    }
};

#endif // HTTP_REQUEST_PROCESSOR_H

