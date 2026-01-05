#ifndef HTTP_REQUEST_PROCESSOR_H
#define HTTP_REQUEST_PROCESSOR_H

#include "IHttpRequestProcessor.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestDispatcher.h"
#include "IHttpResponseQueue.h"
#include <IHttpResponse.h>

/// @Component
class HttpRequestProcessor final : public IHttpRequestProcessor {

    /// @Autowired
    Private IHttpRequestQueuePtr requestQueue;

    /// @Autowired
    Private IHttpRequestDispatcherPtr dispatcher;

    /// @Autowired
    Private IHttpResponseQueuePtr responseQueue;

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
        
        // Dispatch request to get response body
        StdString responseBody = dispatcher->DispatchRequest(request);
        
        // Get request ID from the request
        StdString requestId = StdString(request->GetRequestId());
        if (requestId.empty()) {
            return false;
        }
        
        // Create HTTP response with request ID and response body
        IHttpResponsePtr response = IHttpResponse::GetResponse(requestId, responseBody);
        if (response == nullptr) {
            return false;
        }
        
        // Enqueue response into response queue
        responseQueue->EnqueueResponse(response);
        
        return true;
    }
};

#endif // HTTP_REQUEST_PROCESSOR_H

