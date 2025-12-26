#ifndef HTTP_REQUEST_PROCESSOR_H
#define HTTP_REQUEST_PROCESSOR_H

#include "IHttpRequestProcessor.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestDispatcher.h"

COMPONENT
class HttpRequestProcessor final : public IHttpRequestProcessor {

    AUTOWIRED
    Private IHttpRequestQueuePtr requestQueue;

    AUTOWIRED
    Private IHttpRequestDispatcherPtr dispatcher;

    Public HttpRequestProcessor() = default;
    
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
        
        dispatcher->DispatchRequest(request);
        return true;
    }
};

#endif // HTTP_REQUEST_PROCESSOR_H

