#ifndef I_HTTP_REQUEST_QUEUE_H
#define I_HTTP_REQUEST_QUEUE_H

#include <StandardDefines.h>

// Forward declarations
DefineStandardPointers(IHttpRequestQueue)
class IHttpRequestQueue {

    Public Virtual ~IHttpRequestQueue() = default;

    // ============================================================================
    // HTTP REQUEST QUEUE OPERATIONS
    // ============================================================================
    
    /**
     * @brief Enqueues an HTTP request into the queue
     * @param request Pointer to the HTTP request to enqueue
     */
    Public Virtual Void EnqueueRequest(IHttpRequestPtr request) = 0;
    
    /**
     * @brief Gets and removes the front HTTP request from the queue
     * @return Pointer to the HTTP request, or nullptr if queue is empty
     */
    Public Virtual NoDiscard IHttpRequestPtr DequeueRequest() = 0;
    
    /**
     * @brief Check if the queue is empty
     * @return true if queue is empty, false otherwise
     */
    Public Virtual NoDiscard Bool IsEmpty() const = 0;
    
    /**
     * @brief Check if the queue has items
     * @return true if queue has items, false if empty
     */
    Public Virtual NoDiscard Bool HasRequests() const = 0;
};

#endif // I_HTTP_REQUEST_QUEUE_H

