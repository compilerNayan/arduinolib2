#ifndef HTTP_REQUEST_QUEUE_H
#define HTTP_REQUEST_QUEUE_H

#include "IHttpRequestQueue.h"
#include <queue>

COMPONENT
class HttpRequestQueue final : public IHttpRequestQueue {
    Private std::queue<IHttpRequestPtr> requestQueue;

    Public HttpRequestQueue() = default;
    
    Public ~HttpRequestQueue() override = default;

    // ============================================================================
    // HTTP Request Queue Operations
    // ============================================================================
    
    Public Void EnqueueRequest(IHttpRequestPtr request) override {
        if (request == nullptr) {
            return;
        }
        
        requestQueue.push(request);
    }
    
    Public NoDiscard IHttpRequestPtr DequeueRequest() override {
        if (requestQueue.empty()) {
            return nullptr;
        }
        
        IHttpRequestPtr request = requestQueue.front();
        requestQueue.pop();
        return request;
    }
    
    Public NoDiscard Bool IsEmpty() const override {
        return requestQueue.empty();
    }
    
    Public NoDiscard Bool HasRequests() const override {
        return !requestQueue.empty();
    }
};

#endif // HTTP_REQUEST_QUEUE_H

